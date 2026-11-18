# START_MODULE_CONTRACT
#   PURPOSE: Read and edit the offers of an existing Keitaro campaign's streams.
#   SCOPE: Editor view assembly (streams + per-offer stats), add/remove/set offers, audit log.
#   DEPENDS: M-KEITARO-CLIENT, M-DB
#   LINKS: M-OFFER-EDITOR, V-M-OFFER-EDITOR
# END_MODULE_CONTRACT
#
# START_MODULE_MAP
#   log               - module logger
#   OFFER_SCHEMA      - stream schema that carries offers (landings)
#   STATS_TIMEZONE    - report timezone
#   build_editor_view - campaign streams with offers, shares and stats
#   add_offer         - append offer and rebalance equally
#   remove_offer      - drop offer and rebalance equally
#   set_offers        - manual shares (validated)
#   list_changes      - audit log for a campaign
# END_MODULE_MAP
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError, ValidationFailedError
from app.integrations.keitaro import KeitaroClient
from app.integrations.keitaro.models import KReportRow, KStream
from app.models import OfferChange
from app.schemas.editor import EditorView, OfferRow, OfferStats, StatsInterval, StreamView
from app.services.shares import OfferShare, rebalance, validate_shares

log = logging.getLogger("offer_editor")

OFFER_SCHEMA = "landings"
STATS_TIMEZONE = "Europe/Moscow"


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


def _stream_view(stream: KStream, names: dict[int, str], rows: list[KReportRow]) -> StreamView:
    by_offer = {r.offer_id: r for r in rows if r.stream_id == stream.id}
    offers: list[OfferRow] = []
    for o in stream.offers:
        r = by_offer.get(o.offer_id)
        offers.append(
            OfferRow(
                offer_id=o.offer_id,
                name=names.get(o.offer_id, f"Offer #{o.offer_id}"),
                state="active" if o.state == "active" else "disabled",
                share=o.share,
                stats=_stats(r.clicks, r.conversions, r.revenue, r.profit) if r else _stats(0, 0, 0, 0),
            )
        )
    stream_rows = [r for r in rows if r.stream_id == stream.id]
    totals = _stats(
        sum(r.clicks for r in stream_rows),
        sum(r.conversions for r in stream_rows),
        sum(r.revenue for r in stream_rows),
        sum(r.profit for r in stream_rows),
    )
    return StreamView(
        id=stream.id,
        name=stream.name,
        type=stream.type,
        position=stream.position,
        state=stream.state,
        stream_schema=stream.schema_,
        action_payload=stream.action_payload,
        filters=[_describe_filter(f.name, f.mode, f.payload) for f in stream.filters],
        accepts_offers=stream.schema_ == OFFER_SCHEMA,
        offers=offers,
        totals=totals,
    )


async def _offer_names(keitaro: KeitaroClient) -> dict[int, str]:
    return {o.id: o.name for o in await keitaro.list_offers()}


# START_CONTRACT: build_editor_view
#   PURPOSE: Everything the editor page shows for one campaign.
#   INPUTS: { campaign_id: int, interval: StatsInterval, keitaro: KeitaroClient }
#   OUTPUTS: { EditorView - streams sorted by position, offers with share + stats }
#   SIDE_EFFECTS: none (Keitaro reads only)
# END_CONTRACT: build_editor_view
async def build_editor_view(campaign_id: int, interval: StatsInterval, keitaro: KeitaroClient) -> EditorView:
    campaign = await keitaro.get_campaign(campaign_id)
    streams = sorted(await keitaro.list_streams(campaign_id), key=lambda s: s.position)
    names = await _offer_names(keitaro)
    rows = await keitaro.offer_stats(campaign_id, interval.value, STATS_TIMEZONE)
    return EditorView(
        campaign_id=campaign.id,
        campaign_name=campaign.name,
        alias=campaign.alias,
        interval=interval,
        streams=[_stream_view(s, names, rows) for s in streams],
    )


async def _load_offer_stream(campaign_id: int, stream_id: int, keitaro: KeitaroClient) -> KStream:
    stream = await keitaro.get_stream(stream_id)
    if stream.campaign_id != campaign_id:
        raise NotFoundError(f"Поток {stream_id} не принадлежит кампании {campaign_id}")
    if stream.schema_ != OFFER_SCHEMA:
        raise ValidationFailedError("В этом потоке нет офферов (схема не «Лендинги и офферы»)")
    return stream


def _current(stream: KStream) -> list[OfferShare]:
    return [
        OfferShare(o.offer_id, o.share, "active" if o.state == "active" else "disabled")
        for o in stream.offers
    ]


# START_BLOCK_APPLY
async def _apply(
    campaign_id: int,
    stream: KStream,
    new: list[OfferShare],
    action: str,
    offer_id: int | None,
    keitaro: KeitaroClient,
    session: AsyncSession,
) -> StreamView:
    validate_shares(new)
    before = [o.as_dict() for o in _current(stream)]
    updated = await keitaro.update_stream(stream.id, {"offers": [o.as_dict() for o in new]})
    after = [o.as_dict() for o in _current(updated)]
    session.add(
        OfferChange(
            campaign_id=campaign_id,
            stream_id=stream.id,
            action=action,
            offer_id=offer_id,
            before=before,
            after=after,
        )
    )
    await session.commit()
    log.info("[Editor][%s][BLOCK_APPLY] stream %s offers %s -> %s", action, stream.id, before, after)
    names = await _offer_names(keitaro)
    return _stream_view(updated, names, [])


# END_BLOCK_APPLY


# START_CONTRACT: add_offer
#   PURPOSE: Add offer to a stream; all active offers get equal shares (sum 100).
#   INPUTS: { campaign_id: int, stream_id: int, offer_id: int, keitaro, session }
#   OUTPUTS: { StreamView - updated stream (stats not included) }
#   SIDE_EFFECTS: PUT /streams/{id}; inserts offer_changes row
# END_CONTRACT: add_offer
async def add_offer(
    campaign_id: int, stream_id: int, offer_id: int, keitaro: KeitaroClient, session: AsyncSession
) -> StreamView:
    stream = await _load_offer_stream(campaign_id, stream_id, keitaro)
    current = _current(stream)
    if any(o.offer_id == offer_id for o in current):
        raise ValidationFailedError(f"Оффер {offer_id} уже есть в потоке")
    new = rebalance([*current, OfferShare(offer_id, 0, "active")])
    return await _apply(campaign_id, stream, new, "add", offer_id, keitaro, session)


# START_CONTRACT: remove_offer
#   PURPOSE: Remove offer from a stream; remaining active offers get equal shares.
#   INPUTS: { campaign_id: int, stream_id: int, offer_id: int, keitaro, session }
#   OUTPUTS: { StreamView }
#   SIDE_EFFECTS: PUT /streams/{id}; inserts offer_changes row
# END_CONTRACT: remove_offer
async def remove_offer(
    campaign_id: int, stream_id: int, offer_id: int, keitaro: KeitaroClient, session: AsyncSession
) -> StreamView:
    stream = await _load_offer_stream(campaign_id, stream_id, keitaro)
    current = _current(stream)
    if not any(o.offer_id == offer_id for o in current):
        raise NotFoundError(f"Оффера {offer_id} нет в потоке")
    new = rebalance([o for o in current if o.offer_id != offer_id])
    return await _apply(campaign_id, stream, new, "remove", offer_id, keitaro, session)


# START_CONTRACT: set_offers
#   PURPOSE: Replace stream offers with manual shares (active shares must sum to 100).
#   INPUTS: { campaign_id: int, stream_id: int, offers: list[OfferShare], keitaro, session }
#   OUTPUTS: { StreamView }
#   SIDE_EFFECTS: PUT /streams/{id}; inserts offer_changes row
# END_CONTRACT: set_offers
async def set_offers(
    campaign_id: int, stream_id: int, offers: list[OfferShare], keitaro: KeitaroClient, session: AsyncSession
) -> StreamView:
    stream = await _load_offer_stream(campaign_id, stream_id, keitaro)
    return await _apply(campaign_id, stream, offers, "update", None, keitaro, session)


async def list_changes(campaign_id: int, session: AsyncSession) -> list[OfferChange]:
    result = await session.scalars(
        select(OfferChange).where(OfferChange.campaign_id == campaign_id).order_by(OfferChange.id.desc())
    )
    return list(result)
