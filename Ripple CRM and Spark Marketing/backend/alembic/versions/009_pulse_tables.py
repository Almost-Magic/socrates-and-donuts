"""Ripple Pulse: Sales intelligence tables.

New tables: sales_targets, pulse_snapshots, pulse_actions, pulse_wisdom.

Revision ID: 009_pulse
Revises: 008_channel_dna
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "009_pulse"
down_revision = "008_channel_dna"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sales_targets",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("period_type", sa.String(20), nullable=False, server_default="monthly"),
        sa.Column("period_label", sa.String(50), nullable=False),
        sa.Column("period_start", sa.Date, nullable=False),
        sa.Column("period_end", sa.Date, nullable=False),
        sa.Column("target_value", sa.Float, nullable=False),
        sa.Column("currency", sa.String(10), nullable=False, server_default="AUD"),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_sales_targets_period_start", "sales_targets", ["period_start"])
    op.create_index("ix_sales_targets_period_type", "sales_targets", ["period_type"])

    op.create_table(
        "pulse_snapshots",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("snapshot_date", sa.Date, nullable=False, unique=True),
        sa.Column("data_json", sa.Text, nullable=False),
        sa.Column("ai_commentary_json", sa.Text, nullable=True),
        sa.Column("eod_notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_pulse_snapshots_date", "pulse_snapshots", ["snapshot_date"])

    op.create_table(
        "pulse_actions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("snapshot_date", sa.Date, nullable=False, index=True),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column("estimated_minutes", sa.Integer, nullable=True),
        sa.Column("contact_id", UUID(as_uuid=True), sa.ForeignKey("contacts.id"), nullable=True, index=True),
        sa.Column("deal_id", UUID(as_uuid=True), sa.ForeignKey("deals.id"), nullable=True, index=True),
        sa.Column("priority", sa.Integer, nullable=False, server_default="1"),
        sa.Column("is_completed", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "pulse_wisdom",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("quote", sa.Text, nullable=False),
        sa.Column("author", sa.String(200), nullable=False),
        sa.Column("source", sa.String(300), nullable=True),
        sa.Column("last_shown", sa.Date, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("pulse_wisdom")
    op.drop_table("pulse_actions")
    op.drop_table("pulse_snapshots")
    op.drop_table("sales_targets")
