"""initial: created_campaigns, offer_changes

Revision ID: 0001_initial
Revises:
Create Date: 2026-11-18
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "created_campaigns",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("keitaro_campaign_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("alias", sa.String(length=64), nullable=False),
        sa.Column("country", sa.String(length=2), nullable=False),
        sa.Column("offer_id", sa.Integer(), nullable=False),
        sa.Column("domain_id", sa.Integer(), nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("traffic_source_id", sa.Integer(), nullable=False),
        sa.Column("geo_stream_id", sa.Integer(), nullable=False),
        sa.Column("offer_stream_id", sa.Integer(), nullable=False),
        sa.Column("url", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_created_campaigns")),
    )
    op.create_index(
        op.f("ix_created_campaigns_keitaro_campaign_id"),
        "created_campaigns",
        ["keitaro_campaign_id"],
        unique=True,
    )
    op.create_table(
        "offer_changes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("campaign_id", sa.Integer(), nullable=False),
        sa.Column("stream_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=16), nullable=False),
        sa.Column("offer_id", sa.Integer(), nullable=True),
        sa.Column("before", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("after", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_offer_changes")),
    )
    op.create_index(op.f("ix_offer_changes_campaign_id"), "offer_changes", ["campaign_id"], unique=False)
    op.create_index(op.f("ix_offer_changes_stream_id"), "offer_changes", ["stream_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_offer_changes_stream_id"), table_name="offer_changes")
    op.drop_index(op.f("ix_offer_changes_campaign_id"), table_name="offer_changes")
    op.drop_table("offer_changes")
    op.drop_index(op.f("ix_created_campaigns_keitaro_campaign_id"), table_name="created_campaigns")
    op.drop_table("created_campaigns")
