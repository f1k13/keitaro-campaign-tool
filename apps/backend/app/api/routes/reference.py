# START_MODULE_CONTRACT
#   PURPOSE: HTTP endpoints for creator form reference data.
#   SCOPE: GET /api/reference/*
#   DEPENDS: M-KEITARO-CLIENT, M-BACKEND-CORE
#   LINKS: M-BACKEND-API, V-M-BACKEND-API
# END_MODULE_CONTRACT
#
# START_MODULE_MAP
#   router               - APIRouter /api/reference
#   list_offers          - GET /offers
#   list_domains         - GET /domains
#   list_groups          - GET /groups
#   list_traffic_sources - GET /traffic-sources
#   get_defaults         - GET /defaults
# END_MODULE_MAP
from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.integrations.keitaro import KeitaroClient, get_keitaro_client
from app.schemas.reference import CreatorDefaults, DomainOut, GroupOut, OfferOut, TrafficSourceOut

router = APIRouter(prefix="/api/reference", tags=["reference"])


@router.get("/offers", response_model=list[OfferOut], operation_id="listOffers")
async def list_offers(keitaro: KeitaroClient = Depends(get_keitaro_client)) -> list[OfferOut]:
    return [
        OfferOut(id=o.id, name=o.name, state=o.state, country=o.country or [], group=o.group)
        for o in await keitaro.list_offers()
    ]


@router.get("/domains", response_model=list[DomainOut], operation_id="listDomains")
async def list_domains(keitaro: KeitaroClient = Depends(get_keitaro_client)) -> list[DomainOut]:
    return [
        DomainOut(id=d.id, name=d.name, state=d.state, is_ssl=d.is_ssl) for d in await keitaro.list_domains()
    ]


@router.get("/groups", response_model=list[GroupOut], operation_id="listGroups")
async def list_groups(keitaro: KeitaroClient = Depends(get_keitaro_client)) -> list[GroupOut]:
    return [GroupOut(id=g.id, name=g.name) for g in await keitaro.list_campaign_groups()]


@router.get("/traffic-sources", response_model=list[TrafficSourceOut], operation_id="listTrafficSources")
async def list_traffic_sources(
    keitaro: KeitaroClient = Depends(get_keitaro_client),
) -> list[TrafficSourceOut]:
    return [
        TrafficSourceOut(id=t.id, name=t.name, state=t.state) for t in await keitaro.list_traffic_sources()
    ]


@router.get("/defaults", response_model=CreatorDefaults, operation_id="getCreatorDefaults")
async def get_defaults(settings: Settings = Depends(get_settings)) -> CreatorDefaults:
    return CreatorDefaults(
        domain_id=settings.keitaro_default_domain_id,
        group_id=settings.keitaro_default_group_id,
        traffic_source_id=settings.keitaro_default_traffic_source_id,
        geo_redirect_url=settings.keitaro_geo_redirect_url,
        campaign_name_prefix=settings.campaign_name_prefix,
    )
