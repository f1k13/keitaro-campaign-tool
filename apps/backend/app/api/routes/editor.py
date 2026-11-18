# START_MODULE_CONTRACT
#   PURPOSE: HTTP endpoints for the offer editor of an existing campaign.
#   SCOPE: GET editor view, POST/DELETE/PUT stream offers, GET change log.
#   DEPENDS: M-OFFER-EDITOR, M-KEITARO-CLIENT, M-DB
#   LINKS: M-BACKEND-API, V-M-BACKEND-API
# END_MODULE_CONTRACT
#
# START_MODULE_MAP
#   router       - APIRouter /api/campaigns/{campaign_id}
#   get_editor   - GET .../editor?interval
#   add_offer    - POST .../streams/{stream_id}/offers
#   remove_offer - DELETE .../streams/{stream_id}/offers/{offer_id}
#   set_offers   - PUT .../streams/{stream_id}/offers
#   list_changes - GET .../changes
# END_MODULE_MAP
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.integrations.keitaro import KeitaroClient, get_keitaro_client
from app.schemas.editor import (
    AddOfferRequest,
    EditorView,
    OfferChangeOut,
    SetOffersRequest,
    StatsInterval,
    StreamView,
)
from app.services import offer_editor
from app.services.shares import OfferShare

router = APIRouter(prefix="/api/campaigns/{campaign_id}", tags=["editor"])


@router.get("/editor", response_model=EditorView, operation_id="getEditorView")
async def get_editor(
    campaign_id: int,
    interval: StatsInterval = Query(default=StatsInterval.all_time),
    keitaro: KeitaroClient = Depends(get_keitaro_client),
) -> EditorView:
    return await offer_editor.build_editor_view(campaign_id, interval, keitaro)


@router.post("/streams/{stream_id}/offers", response_model=StreamView, operation_id="addStreamOffer")
async def add_offer(
    campaign_id: int,
    stream_id: int,
    body: AddOfferRequest,
    keitaro: KeitaroClient = Depends(get_keitaro_client),
    session: AsyncSession = Depends(get_session),
) -> StreamView:
    return await offer_editor.add_offer(campaign_id, stream_id, body.offer_id, keitaro, session)


@router.delete(
    "/streams/{stream_id}/offers/{offer_id}", response_model=StreamView, operation_id="removeStreamOffer"
)
async def remove_offer(
    campaign_id: int,
    stream_id: int,
    offer_id: int,
    keitaro: KeitaroClient = Depends(get_keitaro_client),
    session: AsyncSession = Depends(get_session),
) -> StreamView:
    return await offer_editor.remove_offer(campaign_id, stream_id, offer_id, keitaro, session)


@router.put("/streams/{stream_id}/offers", response_model=StreamView, operation_id="setStreamOffers")
async def set_offers(
    campaign_id: int,
    stream_id: int,
    body: SetOffersRequest,
    keitaro: KeitaroClient = Depends(get_keitaro_client),
    session: AsyncSession = Depends(get_session),
) -> StreamView:
    offers = [OfferShare(o.offer_id, o.share, o.state) for o in body.offers]
    return await offer_editor.set_offers(campaign_id, stream_id, offers, keitaro, session)


@router.get("/changes", response_model=list[OfferChangeOut], operation_id="listOfferChanges")
async def list_changes(
    campaign_id: int, session: AsyncSession = Depends(get_session)
) -> list[OfferChangeOut]:
    return [
        OfferChangeOut(
            id=c.id,
            stream_id=c.stream_id,
            action=c.action,
            offer_id=c.offer_id,
            before=c.before,
            after=c.after,
            created_at=c.created_at,
        )
        for c in await offer_editor.list_changes(campaign_id, session)
    ]
