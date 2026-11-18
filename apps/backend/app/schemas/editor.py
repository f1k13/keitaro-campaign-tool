# START_MODULE_CONTRACT
#   PURPOSE: Offer editor DTOs.
#   SCOPE: EditorView, StreamView, OfferRow, OfferStats, offer mutation requests, OfferChangeOut.
#   DEPENDS: none
#   LINKS: M-BACKEND-API, V-M-BACKEND-API
# END_MODULE_CONTRACT
#
# START_MODULE_MAP
#   StatsInterval    - allowed Keitaro report intervals
#   OfferStats       - clicks/conversions/revenue/profit plus CR and EPC
#   OfferRow         - offer inside a stream: status, share, pin, draft flag, stats
#   StreamView       - stream with offers, draft flag and totals
#   EditorView       - campaign + wrapper streams
#   ErrorOut         - error body {detail, code} of domain errors
#   AddOfferRequest  - draft-add one offer by id
#   PinOfferRequest  - draft-pin an offer share (null = current share)
#   OfferChangeOut   - push audit log row
# END_MODULE_MAP
from datetime import datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field


class StatsInterval(StrEnum):
    today = "today"
    yesterday = "yesterday"
    seven_days = "7_days_ago"
    month = "1_month_ago"
    all_time = "all_time"


class OfferStats(BaseModel):
    clicks: int = 0
    conversions: int = 0
    revenue: float = 0
    profit: float = 0
    cr: float = Field(0, description="conversions / clicks * 100")
    epc: float = Field(0, description="revenue / clicks")


class OfferRow(BaseModel):
    offer_id: int
    name: str
    status: Literal["active", "removed"]
    share: int
    pinned: bool = Field(description="Share is fixed and kept through rebalances")
    is_new: bool = Field(description="Added in the draft, not yet pushed to Keitaro")
    stats: OfferStats


class StreamView(BaseModel):
    id: int
    name: str | None
    type: str
    position: int
    state: str
    stream_schema: str | None = Field(description="Keitaro stream schema: redirect | landings | action")
    action_payload: str | None
    filters: list[str]
    accepts_offers: bool
    is_dirty: bool = Field(description="Has unpublished draft changes (shown yellow)")
    published_at: datetime | None
    offers: list[OfferRow]
    totals: OfferStats


class EditorView(BaseModel):
    campaign_id: int
    campaign_name: str
    alias: str
    interval: StatsInterval
    fetched_at: datetime | None
    streams: list[StreamView]


class ErrorOut(BaseModel):
    detail: str
    code: str


class AddOfferRequest(BaseModel):
    offer_id: int = Field(gt=0)


class PinOfferRequest(BaseModel):
    share: int | None = Field(
        default=None, ge=0, le=100, description="Pinned share; null pins the current share"
    )


class OfferChangeOut(BaseModel):
    id: int
    stream_id: int
    action: str
    offer_id: int | None
    before: list[dict[str, Any]]
    after: list[dict[str, Any]]
    created_at: datetime
