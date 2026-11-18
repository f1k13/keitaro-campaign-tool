# START_MODULE_CONTRACT
#   PURPOSE: HTTP endpoints for campaign creation and campaign listing.
#   SCOPE: POST /api/campaigns, GET /api/campaigns, GET /api/campaigns/created
#   DEPENDS: M-CAMPAIGN-CREATOR, M-KEITARO-CLIENT, M-DB
#   LINKS: M-BACKEND-API, V-M-BACKEND-API
# END_MODULE_CONTRACT
#
# START_MODULE_MAP
#   router          - APIRouter /api/campaigns
#   create_campaign - POST /api/campaigns
#   list_campaigns  - GET /api/campaigns?search&limit
#   list_created    - GET /api/campaigns/created
# END_MODULE_MAP
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.session import get_session
from app.integrations.keitaro import KeitaroClient, get_keitaro_client
from app.schemas.campaigns import CampaignCreate, CampaignCreated, CampaignOut, CreatedCampaignOut
from app.services import campaign_creator

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])


@router.post(
    "", response_model=CampaignCreated, status_code=status.HTTP_201_CREATED, operation_id="createCampaign"
)
async def create_campaign(
    body: CampaignCreate,
    keitaro: KeitaroClient = Depends(get_keitaro_client),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> CampaignCreated:
    return await campaign_creator.create_campaign(body, keitaro, session, settings)


@router.get("", response_model=list[CampaignOut], operation_id="listCampaigns")
async def list_campaigns(
    search: str | None = Query(default=None, description="Substring of name, alias or id"),
    limit: int = Query(default=50, ge=1, le=500),
    keitaro: KeitaroClient = Depends(get_keitaro_client),
    session: AsyncSession = Depends(get_session),
) -> list[CampaignOut]:
    created_ids = {c.keitaro_campaign_id for c in await campaign_creator.list_created(session)}
    campaigns = sorted(await keitaro.list_campaigns(), key=lambda c: c.id, reverse=True)
    if search:
        q = search.strip().lower()
        campaigns = [c for c in campaigns if q in c.name.lower() or q in c.alias.lower() or q == str(c.id)]
    return [
        CampaignOut(
            id=c.id,
            name=c.name,
            alias=c.alias,
            state=c.state,
            group=c.group,
            domain=c.domain,
            created_at=c.created_at,
            created_here=c.id in created_ids,
        )
        for c in campaigns[:limit]
    ]


@router.get("/created", response_model=list[CreatedCampaignOut], operation_id="listCreatedCampaigns")
async def list_created(session: AsyncSession = Depends(get_session)) -> list[CreatedCampaignOut]:
    return [
        CreatedCampaignOut(
            keitaro_campaign_id=c.keitaro_campaign_id,
            name=c.name,
            alias=c.alias,
            country=c.country,
            offer_id=c.offer_id,
            url=c.url,
            created_at=c.created_at,
        )
        for c in await campaign_creator.list_created(session)
    ]
