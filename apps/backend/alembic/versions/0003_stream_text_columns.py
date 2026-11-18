"""stream wrapper: unbounded text for Keitaro-provided strings

Revision ID: 0003_stream_text_columns
Revises: 0002_stream_wrapper
Create Date: 2026-11-18
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0003_stream_text_columns"
down_revision: str | None = "0002_stream_wrapper"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Keitaro action payloads (show_html, long redirect macros) and names have no length limit.
    op.alter_column("streams", "name", type_=sa.Text(), existing_nullable=True)
    op.alter_column("streams", "action_payload", type_=sa.Text(), existing_nullable=True)
    op.alter_column("stream_offers", "offer_name", type_=sa.Text(), existing_nullable=False)


def downgrade() -> None:
    op.alter_column("stream_offers", "offer_name", type_=sa.String(length=512), existing_nullable=False)
    op.alter_column("streams", "action_payload", type_=sa.String(length=2048), existing_nullable=True)
    op.alter_column("streams", "name", type_=sa.String(length=255), existing_nullable=True)
