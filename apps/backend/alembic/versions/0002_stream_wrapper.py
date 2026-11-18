"""stream wrapper: streams, stream_offers (draft editing)

Revision ID: 0002_stream_wrapper
Revises: 0001_initial
Create Date: 2026-11-18
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0002_stream_wrapper"
down_revision: str | None = "0001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "streams",
        sa.Column("id", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("campaign_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("type", sa.String(length=32), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("state", sa.String(length=32), nullable=False),
        sa.Column("stream_schema", sa.String(length=32), nullable=True),
        sa.Column("action_payload", sa.String(length=2048), nullable=True),
        sa.Column("filters", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("is_dirty", sa.Boolean(), nullable=False),
        sa.Column("published_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_streams")),
    )
    op.create_index(op.f("ix_streams_campaign_id"), "streams", ["campaign_id"], unique=False)
    op.create_table(
        "stream_offers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("stream_id", sa.Integer(), nullable=False),
        sa.Column("offer_id", sa.Integer(), nullable=False),
        sa.Column("offer_name", sa.String(length=512), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("share", sa.Integer(), nullable=False),
        sa.Column("pinned", sa.Boolean(), nullable=False),
        sa.Column("in_keitaro", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["stream_id"], ["streams.id"], name=op.f("fk_stream_offers_stream_id_streams"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_stream_offers")),
        sa.UniqueConstraint("stream_id", "offer_id", name="uq_stream_offers_stream_id_offer_id"),
    )
    op.create_index(op.f("ix_stream_offers_stream_id"), "stream_offers", ["stream_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_stream_offers_stream_id"), table_name="stream_offers")
    op.drop_table("stream_offers")
    op.drop_index(op.f("ix_streams_campaign_id"), table_name="streams")
    op.drop_table("streams")
