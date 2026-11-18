# START_MODULE_CONTRACT
#   PURPOSE: Audit log of offer edits applied to Keitaro streams.
#   SCOPE: offer_changes table mapping.
#   DEPENDS: M-DB
#   LINKS: M-DB, V-M-DB
# END_MODULE_CONTRACT
#
# START_MODULE_MAP
#   OfferChange - ORM model for offer_changes
# END_MODULE_MAP
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class OfferChange(Base):
    __tablename__ = "offer_changes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    campaign_id: Mapped[int] = mapped_column(Integer, index=True)
    stream_id: Mapped[int] = mapped_column(Integer, index=True)
    action: Mapped[str] = mapped_column(String(16))  # add | remove | update
    offer_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    before: Mapped[list[dict[str, Any]]] = mapped_column(JSONB)
    after: Mapped[list[dict[str, Any]]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
