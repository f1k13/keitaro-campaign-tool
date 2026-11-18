# START_MODULE_CONTRACT
#   PURPOSE: HTTP endpoints for the draft/publish offer editor of an existing campaign.
#   SCOPE: editor view, fetch streams, draft offer actions, push, cancel, change log.
#   DEPENDS: M-OFFER-EDITOR, M-KEITARO-CLIENT, M-DB
#   LINKS: M-BACKEND-API, V-M-BACKEND-API
# END_MODULE_CONTRACT
#
# START_MODULE_MAP
#   router        - APIRouter /api/campaigns/{campaign_id}
#   OFFER         - path template of one offer inside a stream
#   get_editor    - GET .../editor?interval (fetches streams on first open)
#   fetch_streams - POST .../streams/fetch
#   add_offer     - POST .../streams/{stream_id}/offers (draft)
#   remove_offer  - DELETE .../streams/{stream_id}/offers/{offer_id} (draft)
#   restore_offer - POST .../streams/{stream_id}/offers/{offer_id}/restore (draft bring back)
#   pin_offer     - PUT .../streams/{stream_id}/offers/{offer_id}/pin (draft)
#   unpin_offer   - DELETE .../streams/{stream_id}/offers/{offer_id}/pin (draft)
#   push_stream   - POST .../streams/{stream_id}/push (publish to Keitaro)
#   cancel_stream - POST .../streams/{stream_id}/cancel (drop draft)
#   list_changes  - GET .../changes (push log)
# END_MODULE_MAP
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.integrations.keitaro import KeitaroClient, get_keitaro_client
from app.schemas.editor import (
    AddOfferRequest,
    EditorView,
    ErrorOut,
    OfferChangeOut,
    PinOfferRequest,
    StatsInterval,
    StreamView,
)
from app.services import offer_editor

router = APIRouter(prefix="/api/campaigns/{campaign_id}", tags=["editor"])

OFFER = "/streams/{stream_id}/offers/{offer_id}"


@router.get("/editor", response_model=EditorView, operation_id="getEditorView")
async def get_editor(
    campaign_id: int,
    interval: StatsInterval = Query(default=StatsInterval.all_time),
    keitaro: KeitaroClient = Depends(get_keitaro_client),
    session: AsyncSession = Depends(get_session),
) -> EditorView:
    return await offer_editor.build_editor_view(campaign_id, interval, keitaro, session)


@router.post("/streams/fetch", response_model=EditorView, operation_id="fetchStreams")
async def fetch_streams(
    campaign_id: int,
    interval: StatsInterval = Query(default=StatsInterval.all_time),
    keitaro: KeitaroClient = Depends(get_keitaro_client),
    session: AsyncSession = Depends(get_session),
) -> EditorView:
    await offer_editor.fetch_streams(campaign_id, keitaro, session)
    return await offer_editor.build_editor_view(campaign_id, interval, keitaro, session)


@router.post("/streams/{stream_id}/offers", response_model=StreamView, operation_id="addStreamOffer")
async def add_offer(
    campaign_id: int,
    stream_id: int,
    body: AddOfferRequest,
    keitaro: KeitaroClient = Depends(get_keitaro_client),
    session: AsyncSession = Depends(get_session),
) -> StreamView:
    return await offer_editor.add_offer(campaign_id, stream_id, body.offer_id, keitaro, session)


@router.delete(OFFER, response_model=StreamView, operation_id="removeStreamOffer")
async def remove_offer(
    campaign_id: int, stream_id: int, offer_id: int, session: AsyncSession = Depends(get_session)
) -> StreamView:
    return await offer_editor.remove_offer(campaign_id, stream_id, offer_id, session)


@router.post(OFFER + "/restore", response_model=StreamView, operation_id="restoreStreamOffer")
async def restore_offer(
    campaign_id: int, stream_id: int, offer_id: int, session: AsyncSession = Depends(get_session)
) -> StreamView:
    return await offer_editor.restore_offer(campaign_id, stream_id, offer_id, session)


@router.put(OFFER + "/pin", response_model=StreamView, operation_id="pinStreamOffer")
async def pin_offer(
    campaign_id: int,
    stream_id: int,
    offer_id: int,
    body: PinOfferRequest,
    session: AsyncSession = Depends(get_session),
) -> StreamView:
    return await offer_editor.pin_offer(campaign_id, stream_id, offer_id, body.share, session)


@router.delete(OFFER + "/pin", response_model=StreamView, operation_id="unpinStreamOffer")
async def unpin_offer(
    campaign_id: int, stream_id: int, offer_id: int, session: AsyncSession = Depends(get_session)
) -> StreamView:
    return await offer_editor.unpin_offer(campaign_id, stream_id, offer_id, session)


@router.post(
    "/streams/{stream_id}/push",
    response_model=StreamView,
    operation_id="pushStream",
    responses={
        404: {"model": ErrorOut, "description": "Stream not found in the wrapper or in Keitaro"},
        409: {"model": ErrorOut, "description": "Stream changed in Keitaro since the last fetch"},
        502: {"model": ErrorOut, "description": "Keitaro API error"},
    },
)
async def push_stream(
    campaign_id: int,
    stream_id: int,
    keitaro: KeitaroClient = Depends(get_keitaro_client),
    session: AsyncSession = Depends(get_session),
) -> StreamView:
    return await offer_editor.push_stream(campaign_id, stream_id, keitaro, session)


@router.post("/streams/{stream_id}/cancel", response_model=StreamView, operation_id="cancelStream")
async def cancel_stream(
    campaign_id: int, stream_id: int, session: AsyncSession = Depends(get_session)
) -> StreamView:
    return await offer_editor.cancel_stream(campaign_id, stream_id, session)


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
