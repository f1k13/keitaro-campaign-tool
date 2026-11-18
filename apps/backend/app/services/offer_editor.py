# START_MODULE_CONTRACT
#   PURPOSE: Offer editor over a local wrapper of Keitaro streams: draft edits, pinned weights,
#            Push / Cancel publishing and Fetch Streams sync.
#   SCOPE: Only fetch_streams and push_stream talk to Keitaro (plus read-only stats/lookups);
#          every other action edits the wrapper and marks the stream dirty.
#   DEPENDS: M-KEITARO-CLIENT, M-DB
#   LINKS: M-OFFER-EDITOR, V-M-OFFER-EDITOR, DF-EDIT-OFFERS
# END_MODULE_CONTRACT
#
# START_MODULE_MAP
#   log               - module logger
#   OFFER_SCHEMA      - Keitaro stream schema that carries offers ("landings")
#   STATS_TIMEZONE    - timezone for report/build
#   fetch_streams     - pull all campaign streams from Keitaro into the wrapper
#   build_editor_view - wrapper streams + per-offer stats (fetches on first open)
#   add_offer         - draft: add offer by id (brings back a removed one)
#   remove_offer      - draft: grey out offer, share 0
#   restore_offer     - draft: bring back a removed offer
#   pin_offer         - draft: fix an offer's share (value or current)
#   unpin_offer       - draft: release a pinned share
#   push_stream       - publish active offers and shares to Keitaro
#   cancel_stream     - drop the draft, restore last published state
#   list_changes      - push audit log for a campaign
# END_MODULE_MAP
import logging
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError, ConflictError, NotFoundError, ValidationFailedError
from app.integrations.keitaro import KeitaroClient
from app.integrations.keitaro.models import KReportRow, KStream
from app.models import OfferChange, Stream, StreamOffer
from app.models.stream import OFFER_ACTIVE, OFFER_REMOVED
from app.schemas.editor import EditorView, OfferRow, OfferStats, StatsInterval, StreamView
from app.services.shares import ShareSlot, rebalance, validate_publishable

log = logging.getLogger("offer_editor")

OFFER_SCHEMA = "landings"
STATS_TIMEZONE = "Europe/Moscow"


# --- helpers -------------------------------------------------------------------------------------


def _stats(clicks: int, conversions: int, revenue: float, profit: float) -> OfferStats:
    return OfferStats(
        clicks=clicks,
        conversions=conversions,
        revenue=round(revenue, 2),
        profit=round(profit, 2),
        cr=round(conversions / clicks * 100, 2) if clicks else 0,
        epc=round(revenue / clicks, 4) if clicks else 0,
    )


def _describe_filter(name: str, mode: str, payload: object) -> str:
    values = ", ".join(map(str, payload)) if isinstance(payload, list) else str(payload or "")
    sign = "=" if mode == "accept" else "≠"
    return f"{name} {sign} {values}".strip()


def _snapshot(stream: Stream) -> list[dict[str, Any]]:
    return [
        {
            "offer_id": o.offer_id,
            "offer_name": o.offer_name,
            "status": o.status,
            "share": o.share,
            "pinned": o.pinned,
            "in_keitaro": o.in_keitaro,
        }
        for o in stream.offers
    ]


def _view(stream: Stream, rows: list[KReportRow]) -> StreamView:
    by_offer = {r.offer_id: r for r in rows if r.stream_id == stream.id}
    zero = _stats(0, 0, 0, 0)
    offers: list[OfferRow] = []
    for o in stream.offers:
        r = by_offer.get(o.offer_id)
        offers.append(
            OfferRow(
                offer_id=o.offer_id,
                name=o.offer_name,
                status="active" if o.status == OFFER_ACTIVE else "removed",
                share=o.share,
                pinned=o.pinned,
                is_new=o.status == OFFER_ACTIVE and not o.in_keitaro,
                stats=_stats(r.clicks, r.conversions, r.revenue, r.profit) if r else zero,
            )
        )
    stream_rows = [r for r in rows if r.stream_id == stream.id]
    return StreamView(
        id=stream.id,
        name=stream.name,
        type=stream.type,
        position=stream.position,
        state=stream.state,
        stream_schema=stream.stream_schema,
        action_payload=stream.action_payload,
        filters=list(stream.filters),
        accepts_offers=stream.stream_schema == OFFER_SCHEMA,
        is_dirty=stream.is_dirty,
        published_at=stream.published_at,
        offers=offers,
        totals=_stats(
            sum(r.clicks for r in stream_rows),
            sum(r.conversions for r in stream_rows),
            sum(r.revenue for r in stream_rows),
            sum(r.profit for r in stream_rows),
        ),
    )


async def _offer_names(keitaro: KeitaroClient) -> dict[int, str]:
    return {o.id: o.name for o in await keitaro.list_offers()}


async def _campaign_streams(campaign_id: int, session: AsyncSession, *, lock: bool = False) -> list[Stream]:
    query = select(Stream).where(Stream.campaign_id == campaign_id).order_by(Stream.position, Stream.id)
    if lock:
        # serialise with draft actions / push / cancel, which lock single stream rows
        query = query.with_for_update().execution_options(populate_existing=True)
    result = await session.scalars(query)
    return list(result)


# START_BLOCK_SYNC_OFFERS
def _sync_offers(stream: Stream, kstream: KStream, names: dict[int, str]) -> None:
    """Make wrapper offers mirror Keitaro (used by fetch on clean streams and after push)."""
    remote = {o.offer_id: o for o in kstream.offers}
    local = {o.offer_id: o for o in stream.offers}
    for offer_id, row in local.items():
        k = remote.get(offer_id)
        if row.offer_name.startswith("Offer #") and offer_id in names:
            row.offer_name = names[offer_id]
        if k is not None and k.state == "active":
            row.status, row.share, row.in_keitaro = OFFER_ACTIVE, k.share, True
        else:
            # gone from Keitaro (or disabled there): grey out, keep for bring back
            row.status, row.share, row.pinned = OFFER_REMOVED, 0, False
            row.in_keitaro = k is not None
    for offer_id, k in remote.items():
        if offer_id in local:
            continue
        active = k.state == "active"
        stream.offers.append(
            StreamOffer(
                offer_id=offer_id,
                offer_name=names.get(offer_id, f"Offer #{offer_id}"),
                status=OFFER_ACTIVE if active else OFFER_REMOVED,
                share=k.share if active else 0,
                pinned=False,
                in_keitaro=True,
            )
        )
    stream.is_dirty = False
    stream.published_snapshot = _snapshot(stream)


# END_BLOCK_SYNC_OFFERS


def _apply_meta(stream: Stream, k: KStream) -> None:
    stream.campaign_id = k.campaign_id
    stream.name = k.name
    stream.type = k.type
    stream.position = k.position
    stream.state = k.state
    stream.stream_schema = k.schema_
    stream.action_payload = k.action_payload or None
    stream.filters = [_describe_filter(f.name, f.mode, f.payload) for f in k.filters]


# --- fetch / view --------------------------------------------------------------------------------


# START_CONTRACT: fetch_streams
#   PURPOSE: Fetch Streams: pull every stream of the campaign from Keitaro into the wrapper.
#   INPUTS: { campaign_id: int, keitaro: KeitaroClient, session: AsyncSession }
#   OUTPUTS: { list[Stream] - wrapper streams ordered by position }
#   SIDE_EFFECTS: locks the campaign stream rows; upserts streams; clean offer streams mirror Keitaro
#                 (offers gone from Keitaro become removed); dirty streams keep their draft offers;
#                 streams deleted in Keitaro are dropped; a concurrent first fetch is tolerated
# END_CONTRACT: fetch_streams
async def fetch_streams(campaign_id: int, keitaro: KeitaroClient, session: AsyncSession) -> list[Stream]:
    await keitaro.get_campaign(campaign_id)  # 404 if the campaign does not exist
    remote = await keitaro.list_streams(campaign_id)
    names = await _offer_names(keitaro)
    local = {s.id: s for s in await _campaign_streams(campaign_id, session, lock=True)}

    # START_BLOCK_FETCH
    for k in remote:
        stream = local.pop(k.id, None)
        if stream is None:
            stream = Stream(id=k.id, is_dirty=False, published_snapshot=[], offers=[])
            session.add(stream)
        _apply_meta(stream, k)
        stream.fetched_at = datetime.now(UTC)
        if stream.stream_schema != OFFER_SCHEMA:
            if stream.is_dirty:
                # no offers to publish any more: drop the draft instead of leaving it stuck
                stream.offers[:] = [o for o in stream.offers if o.in_keitaro]
                stream.is_dirty = False
        elif not stream.is_dirty:
            _sync_offers(stream, k, names)
    for gone in local.values():
        await session.delete(gone)
    try:
        await session.commit()
    except IntegrityError:
        # a concurrent first fetch inserted the same streams; its result is just as fresh
        await session.rollback()
        log.info("[Editor][fetch_streams][BLOCK_FETCH] campaign %s fetched concurrently", campaign_id)
    log.info("[Editor][fetch_streams][BLOCK_FETCH] campaign %s: %s streams", campaign_id, len(remote))
    # END_BLOCK_FETCH
    return await _campaign_streams(campaign_id, session)


# START_CONTRACT: build_editor_view
#   PURPOSE: Everything the editor page shows for one campaign.
#   INPUTS: { campaign_id: int, interval: StatsInterval, keitaro, session }
#   OUTPUTS: { EditorView - wrapper streams (fetched from Keitaro on first open) + report stats }
#   SIDE_EFFECTS: first open performs fetch_streams; otherwise Keitaro reads only
# END_CONTRACT: build_editor_view
async def build_editor_view(
    campaign_id: int, interval: StatsInterval, keitaro: KeitaroClient, session: AsyncSession
) -> EditorView:
    campaign = await keitaro.get_campaign(campaign_id)
    streams = await _campaign_streams(campaign_id, session)
    if not streams:
        streams = await fetch_streams(campaign_id, keitaro, session)
    rows = await keitaro.offer_stats(campaign_id, interval.value, STATS_TIMEZONE)
    fetched = [s.fetched_at for s in streams]
    return EditorView(
        campaign_id=campaign.id,
        campaign_name=campaign.name,
        alias=campaign.alias,
        interval=interval,
        fetched_at=min(fetched) if fetched else None,
        streams=[_view(s, rows) for s in streams],
    )


# --- draft actions -------------------------------------------------------------------------------


async def _offer_stream(
    campaign_id: int, stream_id: int, session: AsyncSession, *, require_offers: bool = True
) -> Stream:
    # FOR UPDATE serialises concurrent draft actions on one stream (no lost rebalance)
    stream = await session.get(Stream, stream_id, with_for_update=True, populate_existing=True)
    if stream is None or stream.campaign_id != campaign_id:
        raise NotFoundError(f"Поток {stream_id} не найден в кампании {campaign_id}, нажмите Fetch Streams")
    if require_offers and stream.stream_schema != OFFER_SCHEMA:
        raise ValidationFailedError("В этом потоке нет офферов (схема не «Лендинги и офферы»)")
    return stream


def _row(stream: Stream, offer_id: int) -> StreamOffer:
    for o in stream.offers:
        if o.offer_id == offer_id:
            return o
    raise NotFoundError(f"Оффера {offer_id} нет в потоке")


# START_BLOCK_REBALANCE
async def _rebalance_and_save(stream: Stream, session: AsyncSession, action: str) -> StreamView:
    slots = [ShareSlot(o.offer_id, o.share, o.status == OFFER_ACTIVE, o.pinned) for o in stream.offers]
    for o, s in zip(stream.offers, rebalance(slots), strict=True):
        o.share, o.pinned = s.share, s.pinned
    stream.is_dirty = True
    await session.commit()
    await session.refresh(stream, attribute_names=["offers"])
    log.info(
        "[Editor][%s][BLOCK_REBALANCE] stream %s draft %s",
        action,
        stream.id,
        [(o.offer_id, o.status, o.share, o.pinned) for o in stream.offers],
    )
    return _view(stream, [])


# END_BLOCK_REBALANCE


# START_CONTRACT: add_offer
#   PURPOSE: Draft-add an offer; equal split among unpinned active offers. A removed offer is brought back.
#   INPUTS: { campaign_id, stream_id, offer_id: int, keitaro, session }
#   OUTPUTS: { StreamView - stats not included }
#   SIDE_EFFECTS: Keitaro read (offer lookup); wrapper write; stream marked dirty
# END_CONTRACT: add_offer
async def add_offer(
    campaign_id: int, stream_id: int, offer_id: int, keitaro: KeitaroClient, session: AsyncSession
) -> StreamView:
    stream = await _offer_stream(campaign_id, stream_id, session)
    existing = next((o for o in stream.offers if o.offer_id == offer_id), None)
    if existing is not None:
        if existing.status == OFFER_ACTIVE:
            raise ValidationFailedError(f"Оффер {offer_id} уже есть в потоке")
        existing.status = OFFER_ACTIVE
        return await _rebalance_and_save(stream, session, "add_offer")
    try:
        offer = await keitaro.get_offer(offer_id)
    except NotFoundError as exc:
        raise ValidationFailedError(f"Оффер {offer_id} не найден в Keitaro") from exc
    name = offer.name if offer else (await _offer_names(keitaro)).get(offer_id, f"Offer #{offer_id}")
    stream.offers.append(
        StreamOffer(
            offer_id=offer_id, offer_name=name, status=OFFER_ACTIVE, share=0, pinned=False, in_keitaro=False
        )
    )
    return await _rebalance_and_save(stream, session, "add_offer")


# START_CONTRACT: remove_offer
#   PURPOSE: Draft-remove: offer turns grey with share 0 and can be brought back.
#   INPUTS: { campaign_id, stream_id, offer_id: int, session }
#   OUTPUTS: { StreamView }
#   SIDE_EFFECTS: wrapper write; stream marked dirty
# END_CONTRACT: remove_offer
async def remove_offer(campaign_id: int, stream_id: int, offer_id: int, session: AsyncSession) -> StreamView:
    stream = await _offer_stream(campaign_id, stream_id, session)
    row = _row(stream, offer_id)
    if row.status == OFFER_REMOVED:
        raise ValidationFailedError(f"Оффер {offer_id} уже удалён")
    row.status = OFFER_REMOVED
    return await _rebalance_and_save(stream, session, "remove_offer")


# START_CONTRACT: restore_offer
#   PURPOSE: Draft bring back of a removed offer.
#   INPUTS: { campaign_id, stream_id, offer_id: int, session }
#   OUTPUTS: { StreamView }
#   SIDE_EFFECTS: wrapper write; stream marked dirty
# END_CONTRACT: restore_offer
async def restore_offer(campaign_id: int, stream_id: int, offer_id: int, session: AsyncSession) -> StreamView:
    stream = await _offer_stream(campaign_id, stream_id, session)
    row = _row(stream, offer_id)
    if row.status == OFFER_ACTIVE:
        raise ValidationFailedError(f"Оффер {offer_id} уже активен")
    row.status = OFFER_ACTIVE
    return await _rebalance_and_save(stream, session, "restore_offer")


# START_CONTRACT: pin_offer
#   PURPOSE: Draft pin: the offer keeps `share` (or its current share) through later rebalances.
#   INPUTS: { campaign_id, stream_id, offer_id: int, share: int | None (0..100), session }
#   OUTPUTS: { StreamView }
#   SIDE_EFFECTS: wrapper write; stream marked dirty; 422 if pinned sum would exceed 100
# END_CONTRACT: pin_offer
async def pin_offer(
    campaign_id: int, stream_id: int, offer_id: int, share: int | None, session: AsyncSession
) -> StreamView:
    stream = await _offer_stream(campaign_id, stream_id, session)
    row = _row(stream, offer_id)
    if row.status != OFFER_ACTIVE:
        raise ValidationFailedError("Запинить можно только активный оффер")
    if share is not None:
        row.share = share
    row.pinned = True
    return await _rebalance_and_save(stream, session, "pin_offer")


# START_CONTRACT: unpin_offer
#   PURPOSE: Draft unpin: the offer rejoins the equal split.
#   INPUTS: { campaign_id, stream_id, offer_id: int, session }
#   OUTPUTS: { StreamView }
#   SIDE_EFFECTS: wrapper write; stream marked dirty
# END_CONTRACT: unpin_offer
async def unpin_offer(campaign_id: int, stream_id: int, offer_id: int, session: AsyncSession) -> StreamView:
    stream = await _offer_stream(campaign_id, stream_id, session)
    _row(stream, offer_id).pinned = False
    return await _rebalance_and_save(stream, session, "unpin_offer")


# --- publish -------------------------------------------------------------------------------------


def _keitaro_state(kstream: KStream) -> set[tuple[int, int, bool]]:
    return {(o.offer_id, o.share if o.state == "active" else 0, o.state == "active") for o in kstream.offers}


def _snapshot_state(stream: Stream) -> set[tuple[int, int, bool]]:
    # what Keitaro looked like at the last fetch/push: only rows that were present there
    return {
        (s["offer_id"], s["share"] if s["status"] == OFFER_ACTIVE else 0, s["status"] == OFFER_ACTIVE)
        for s in stream.published_snapshot
        if s["in_keitaro"]
    }


# START_CONTRACT: push_stream
#   PURPOSE: Publish the draft: Keitaro receives exactly the active offers with their shares.
#   INPUTS: { campaign_id, stream_id, keitaro, session }
#   OUTPUTS: { StreamView }
#   SIDE_EFFECTS: 422 unless >=1 active offer and active shares sum to 100; 409 if Keitaro offers differ
#                 from the published snapshot (changed outside the tool); PUT /streams/{id};
#                 wrapper re-synced from the Keitaro response (removed offers stay removed);
#                 offer_changes row; dirty cleared
# END_CONTRACT: push_stream
async def push_stream(
    campaign_id: int, stream_id: int, keitaro: KeitaroClient, session: AsyncSession
) -> StreamView:
    stream = await _offer_stream(campaign_id, stream_id, session)
    active = [o for o in stream.offers if o.status == OFFER_ACTIVE]
    validate_publishable([ShareSlot(o.offer_id, o.share, True, o.pinned) for o in active])

    # START_BLOCK_PUSH
    try:
        names = await _offer_names(keitaro)
    except AppError:
        names = {}  # names are cosmetic; never fail a push (or lose its audit row) because of them
    before_k = await keitaro.get_stream(stream_id)
    if _keitaro_state(before_k) != _snapshot_state(stream):
        log.warning("[Editor][push_stream][BLOCK_PUSH] stream %s changed in Keitaro since fetch", stream_id)
        raise ConflictError(
            "Поток изменён в Keitaro после последнего Fetch Streams. "
            "Нажмите Cancel, затем Fetch Streams и повторите правки"
        )
    before = [{"offer_id": o.offer_id, "share": o.share, "state": o.state} for o in before_k.offers]
    payload = [{"offer_id": o.offer_id, "share": o.share, "state": "active"} for o in active]
    updated = await keitaro.update_stream(stream_id, {"offers": payload})
    after = [{"offer_id": o.offer_id, "share": o.share, "state": o.state} for o in updated.offers]
    for o in stream.offers:
        names.setdefault(o.offer_id, o.offer_name)
    _sync_offers(stream, updated, names)
    stream.published_at = datetime.now(UTC)
    session.add(
        OfferChange(
            campaign_id=campaign_id,
            stream_id=stream_id,
            action="push",
            offer_id=None,
            before=before,
            after=after,
        )
    )
    await session.commit()
    await session.refresh(stream, attribute_names=["offers"])
    log.info("[Editor][push_stream][BLOCK_PUSH] stream %s: %s -> %s", stream_id, before, after)
    # END_BLOCK_PUSH
    return _view(stream, [])


# START_CONTRACT: cancel_stream
#   PURPOSE: Drop the draft: restore offers, shares and pins of the last fetch/push snapshot.
#   INPUTS: { campaign_id, stream_id, session }
#   OUTPUTS: { StreamView }
#   SIDE_EFFECTS: offers added in the draft are deleted from the wrapper; dirty cleared; works for any schema
# END_CONTRACT: cancel_stream
async def cancel_stream(campaign_id: int, stream_id: int, session: AsyncSession) -> StreamView:
    stream = await _offer_stream(campaign_id, stream_id, session, require_offers=False)
    snapshot = {s["offer_id"]: s for s in stream.published_snapshot}
    for o in list(stream.offers):
        snap = snapshot.get(o.offer_id)
        if snap is None:
            stream.offers.remove(o)
        else:
            o.status, o.share, o.pinned, o.in_keitaro = (
                snap["status"],
                snap["share"],
                snap["pinned"],
                snap["in_keitaro"],
            )
    stream.is_dirty = False
    await session.commit()
    await session.refresh(stream, attribute_names=["offers"])
    log.info("[Editor][cancel_stream][BLOCK_REBALANCE] stream %s restored to snapshot", stream_id)
    return _view(stream, [])


async def list_changes(campaign_id: int, session: AsyncSession) -> list[OfferChange]:
    result = await session.scalars(
        select(OfferChange).where(OfferChange.campaign_id == campaign_id).order_by(OfferChange.id.desc())
    )
    return list(result)
