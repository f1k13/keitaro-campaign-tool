# START_MODULE_CONTRACT
#   PURPOSE: Create a Keitaro campaign with a geo->Google stream and an offer stream.
#   SCOPE: Orchestrates Keitaro calls, name prefixing, rollback on partial failure, local history row.
#   DEPENDS: M-KEITARO-CLIENT, M-DB, M-BACKEND-CORE
#   LINKS: M-CAMPAIGN-CREATOR, V-M-CAMPAIGN-CREATOR
# END_MODULE_CONTRACT
#
# START_MODULE_MAP
#   log             - module logger
#   apply_name_prefix - prepend CAMPAIGN_NAME_PREFIX unless already present
#   create_campaign - full creation flow, returns CampaignCreated
#   list_created    - local history of created campaigns
# END_MODULE_MAP
import logging
import secrets
import string

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.errors import AppError, ValidationFailedError
from app.integrations.keitaro import KeitaroClient
from app.models import CreatedCampaign
from app.schemas.campaigns import CampaignCreate, CampaignCreated

log = logging.getLogger("campaign_creator")

_ALIAS_ALPHABET = string.ascii_letters + string.digits


def _alias() -> str:
    return "".join(secrets.choice(_ALIAS_ALPHABET) for _ in range(8))


# START_CONTRACT: apply_name_prefix
#   PURPOSE: Prepend the configured prefix unless the name already starts with it.
#   INPUTS: { name: str - user input, prefix: str - CAMPAIGN_NAME_PREFIX }
#   OUTPUTS: { str - e.g. campaign1 -> test_ponomaryov_campaign1 }
#   SIDE_EFFECTS: none
# END_CONTRACT: apply_name_prefix
def apply_name_prefix(name: str, prefix: str) -> str:
    return name if not prefix or name.startswith(prefix) else f"{prefix}{name}"


def _resolve(value: int | None, default: int | None, label: str) -> int:
    resolved = value or default
    if not resolved:
        raise ValidationFailedError(f"Не выбран {label} и не задан default в .env")
    return resolved


# START_CONTRACT: create_campaign
#   PURPOSE: Create campaign + 2 streams in Keitaro and remember it locally.
#   INPUTS: { data: CampaignCreate, keitaro: KeitaroClient, session: AsyncSession, settings: Settings }
#   OUTPUTS: { CampaignCreated }
#   SIDE_EFFECTS: POST /campaigns, 2x POST /streams; on stream failure DELETE /campaigns/{id};
#                 inserts created_campaigns row
# END_CONTRACT: create_campaign
async def create_campaign(
    data: CampaignCreate, keitaro: KeitaroClient, session: AsyncSession, settings: Settings
) -> CampaignCreated:
    domain_id = _resolve(data.domain_id, settings.keitaro_default_domain_id, "домен")
    group_id = _resolve(data.group_id, settings.keitaro_default_group_id, "группа")
    source_id = _resolve(data.traffic_source_id, settings.keitaro_default_traffic_source_id, "источник")

    # START_BLOCK_CREATE_CAMPAIGN
    campaign = await keitaro.create_campaign(
        {
            "name": apply_name_prefix(data.name, settings.campaign_name_prefix),
            "alias": _alias(),
            "type": "position",
            "state": "active",
            "cost_type": "CPC",
            "cost_value": 0,
            "cost_currency": "USD",
            "cost_auto": True,
            "uniqueness_method": "ip",
            "cookies_ttl": 24,
            "domain_id": domain_id,
            "group_id": group_id,
            "traffic_source_id": source_id,
        }
    )
    log.info("[Creator][create][BLOCK_CREATE_CAMPAIGN] campaign %s created", campaign.id)
    # END_BLOCK_CREATE_CAMPAIGN

    # START_BLOCK_CREATE_STREAMS
    try:
        geo_stream = await keitaro.create_stream(
            {
                "campaign_id": campaign.id,
                "type": "forced",
                "name": f"Geo {data.country} → Google",
                "position": 1,
                "state": "active",
                "schema": "redirect",
                "action_type": "http",
                "action_payload": settings.keitaro_geo_redirect_url,
                "collect_clicks": True,
                "filter_or": False,
                "filters": [{"name": "country", "mode": "accept", "payload": [data.country]}],
            }
        )
        offer_stream = await keitaro.create_stream(
            {
                "campaign_id": campaign.id,
                "type": "regular",
                "name": "Offers",
                "position": 2,
                "state": "active",
                "schema": "landings",
                "action_type": "http",
                "collect_clicks": True,
                "filter_or": False,
                "filters": [],
                "offers": [{"offer_id": data.offer_id, "share": 100, "state": "active"}],
            }
        )
    except AppError:
        log.warning("[Creator][create][BLOCK_CREATE_STREAMS] rollback campaign %s", campaign.id)
        try:
            await keitaro.delete_campaign(campaign.id)
        except AppError:
            log.exception("[Creator][create][BLOCK_CREATE_STREAMS] rollback failed for %s", campaign.id)
        raise
    # END_BLOCK_CREATE_STREAMS

    full = await keitaro.get_campaign(campaign.id)
    url = f"{full.domain.rstrip('/')}/{full.alias}" if full.domain else None

    # START_BLOCK_PERSIST
    session.add(
        CreatedCampaign(
            keitaro_campaign_id=campaign.id,
            name=campaign.name,
            alias=campaign.alias,
            country=data.country,
            offer_id=data.offer_id,
            domain_id=domain_id,
            group_id=group_id,
            traffic_source_id=source_id,
            geo_stream_id=geo_stream.id,
            offer_stream_id=offer_stream.id,
            url=url,
        )
    )
    await session.commit()
    # END_BLOCK_PERSIST

    return CampaignCreated(
        campaign_id=campaign.id,
        alias=campaign.alias,
        name=campaign.name,
        url=url,
        country=data.country,
        offer_id=data.offer_id,
        domain_id=domain_id,
        group_id=group_id,
        traffic_source_id=source_id,
        geo_stream_id=geo_stream.id,
        offer_stream_id=offer_stream.id,
    )


async def list_created(session: AsyncSession) -> list[CreatedCampaign]:
    result = await session.scalars(select(CreatedCampaign).order_by(CreatedCampaign.id.desc()))
    return list(result)
