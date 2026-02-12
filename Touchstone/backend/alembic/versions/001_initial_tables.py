"""Initial Touchstone tables.

Revision ID: 001
Revises:
Create Date: 2026-02-12
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Contacts
    op.create_table(
        "touchstone_contacts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("anonymous_id", sa.String(64), index=True),
        sa.Column("email", sa.String(255), unique=True, index=True),
        sa.Column("name", sa.String(255)),
        sa.Column("company", sa.String(255)),
        sa.Column("metadata", JSONB, server_default=sa.text("'{}'")),
        sa.Column("identified_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Campaigns
    op.create_table(
        "touchstone_campaigns",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("channel", sa.String(50)),
        sa.Column("start_date", sa.Date()),
        sa.Column("end_date", sa.Date()),
        sa.Column("budget", sa.Numeric(12, 2)),
        sa.Column("currency", sa.String(3), server_default="AUD"),
        sa.Column("metadata", JSONB, server_default=sa.text("'{}'")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Touchpoints
    op.create_table(
        "touchstone_touchpoints",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("contact_id", UUID(as_uuid=True), sa.ForeignKey("touchstone_contacts.id"), index=True),
        sa.Column("anonymous_id", sa.String(64), index=True),
        sa.Column("campaign_id", UUID(as_uuid=True), sa.ForeignKey("touchstone_campaigns.id")),
        sa.Column("channel", sa.String(50)),
        sa.Column("source", sa.String(100)),
        sa.Column("medium", sa.String(100)),
        sa.Column("utm_campaign", sa.String(255)),
        sa.Column("utm_content", sa.String(255)),
        sa.Column("utm_term", sa.String(255)),
        sa.Column("touchpoint_type", sa.String(50), server_default="page_view"),
        sa.Column("page_url", sa.Text()),
        sa.Column("referrer_url", sa.Text()),
        sa.Column("metadata", JSONB, server_default=sa.text("'{}'")),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Deals
    op.create_table(
        "touchstone_deals",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("contact_id", UUID(as_uuid=True), sa.ForeignKey("touchstone_contacts.id"), index=True),
        sa.Column("crm_deal_id", sa.String(255), unique=True),
        sa.Column("deal_name", sa.String(255)),
        sa.Column("amount", sa.Numeric(12, 2)),
        sa.Column("currency", sa.String(3), server_default="AUD"),
        sa.Column("stage", sa.String(50), server_default="open"),
        sa.Column("closed_at", sa.DateTime(timezone=True)),
        sa.Column("crm_source", sa.String(50)),
        sa.Column("metadata", JSONB, server_default=sa.text("'{}'")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Attributions (schema for Phase 2)
    op.create_table(
        "touchstone_attributions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("deal_id", UUID(as_uuid=True), sa.ForeignKey("touchstone_deals.id"), index=True),
        sa.Column("touchpoint_id", UUID(as_uuid=True), sa.ForeignKey("touchstone_touchpoints.id")),
        sa.Column("campaign_id", UUID(as_uuid=True), sa.ForeignKey("touchstone_campaigns.id")),
        sa.Column("model", sa.String(50), nullable=False),
        sa.Column("attributed_amount", sa.Numeric(12, 2)),
        sa.Column("attribution_weight", sa.Numeric(5, 4)),
        sa.Column("calculated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Performance indexes
    op.create_index("ix_touchpoints_timestamp", "touchstone_touchpoints", ["timestamp"])
    op.create_index("ix_touchpoints_type", "touchstone_touchpoints", ["touchpoint_type"])
    op.create_index("ix_deals_stage", "touchstone_deals", ["stage"])
    op.create_index("ix_attributions_model", "touchstone_attributions", ["model"])


def downgrade() -> None:
    op.drop_table("touchstone_attributions")
    op.drop_table("touchstone_deals")
    op.drop_table("touchstone_touchpoints")
    op.drop_table("touchstone_campaigns")
    op.drop_table("touchstone_contacts")
