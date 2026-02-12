"""Phase 2.2: Channel DNA v1 Enhancement.

New table: channel_interactions.
New column: contacts.preferred_times_json.

Revision ID: 008_channel_dna
Revises: 007_meetings
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "008_channel_dna"
down_revision = "007_meetings"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "channel_interactions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("contact_id", UUID(as_uuid=True), sa.ForeignKey("contacts.id"), nullable=False, index=True),
        sa.Column("channel", sa.String(50), nullable=False, index=True),
        sa.Column("direction", sa.String(10), nullable=False, server_default="out"),
        sa.Column("occurred_at", sa.DateTime(timezone=True), server_default=sa.func.now(), index=True),
        sa.Column("response_time_seconds", sa.Integer, nullable=True),
        sa.Column("responded", sa.Boolean, server_default=sa.text("false")),
        sa.Column("day_of_week", sa.Integer, nullable=True),
        sa.Column("hour_of_day", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.add_column("contacts", sa.Column("preferred_times_json", sa.Text, nullable=True))


def downgrade() -> None:
    op.drop_column("contacts", "preferred_times_json")
    op.drop_table("channel_interactions")
