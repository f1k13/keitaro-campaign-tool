# START_MODULE_CONTRACT
#   PURPOSE: Local wrapper of Keitaro streams and their offers holding unpublished drafts.
#   SCOPE: streams and stream_offers table mappings.
#   DEPENDS: M-DB
#   LINKS: M-DB, V-M-DB, M-OFFER-EDITOR
# END_MODULE_CONTRACT
#
# START_MODULE_MAP
#   OFFER_ACTIVE  - status of an offer that is (or will be after Push) in Keitaro
#   OFFER_REMOVED - status of a greyed-out offer (share 0, can be brought back)
#   Stream        - one Keitaro stream (id = Keitaro stream id) with draft flag and published snapshot
#   StreamOffer   - one offer binding inside a wrapped stream
# END_MODULE_MAP
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

OFFER_ACTIVE = "active"
OFFER_REMOVED = "removed"


class Stream(Base):
    __tablename__ = "streams"

    # Keitaro stream id, not autoincrement
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    campaign_id: Mapped[int] = mapped_column(Integer, index=True)
    name: Mapped[str | None] = mapped_column(Text, nullable=True)
    type: Mapped[str] = mapped_column(String(32))
    position: Mapped[int] = mapped_column(Integer)
    state: Mapped[str] = mapped_column(String(32))
    stream_schema: Mapped[str | None] = mapped_column(String(32), nullable=True)
    action_payload: Mapped[str | None] = mapped_column(Text, nullable=True)
    filters: Mapped[list[str]] = mapped_column(JSONB, default=list)
    is_dirty: Mapped[bool] = mapped_column(Boolean, default=False)
    # [{offer_id, offer_name, status, share, pinned, in_keitaro}] at last fetch/push; Cancel restores it
    published_snapshot: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=list)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    offers: Mapped[list["StreamOffer"]] = relationship(
        back_populates="stream", cascade="all, delete-orphan", order_by="StreamOffer.id", lazy="selectin"
    )


class StreamOffer(Base):
    __tablename__ = "stream_offers"
    __table_args__ = (UniqueConstraint("stream_id", "offer_id", name="uq_stream_offers_stream_id_offer_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    stream_id: Mapped[int] = mapped_column(ForeignKey("streams.id", ondelete="CASCADE"), index=True)
    offer_id: Mapped[int] = mapped_column(Integer)
    offer_name: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(16), default=OFFER_ACTIVE)
    share: Mapped[int] = mapped_column(Integer, default=0)
    pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    # True when the offer is currently present in Keitaro (as of last fetch/push)
    in_keitaro: Mapped[bool] = mapped_column(Boolean, default=False)

    stream: Mapped[Stream] = relationship(back_populates="offers")
