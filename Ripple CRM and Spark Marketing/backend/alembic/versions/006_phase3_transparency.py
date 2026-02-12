"""Phase 3: deal_id on emails, consent_preferences, dsar_requests.

Revision ID: 006_phase3
Revises: 005_emails
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "006_phase3"
down_revision = "005_emails"


def upgrade():
    # Add deal_id to emails table
    op.add_column(
        "emails",
        sa.Column("deal_id", UUID(as_uuid=True), sa.ForeignKey("deals.id"), nullable=True, index=True),
    )

    # Consent preferences — per-contact structured preferences
    op.create_table(
        "consent_preferences",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("contact_id", UUID(as_uuid=True), sa.ForeignKey("contacts.id"), nullable=False, index=True),
        sa.Column("email_marketing", sa.Boolean, default=False),
        sa.Column("data_processing", sa.Boolean, default=True),
        sa.Column("third_party_sharing", sa.Boolean, default=False),
        sa.Column("analytics", sa.Boolean, default=True),
        sa.Column("profiling", sa.Boolean, default=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_consent_preferences_contact_id_unique", "consent_preferences", ["contact_id"], unique=True)

    # DSAR requests — formal request tracking
    op.create_table(
        "dsar_requests",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("contact_id", UUID(as_uuid=True), sa.ForeignKey("contacts.id"), nullable=False, index=True),
        sa.Column("request_type", sa.String(30), nullable=False),  # access, export, deletion, rectification
        sa.Column("status", sa.String(20), default="pending"),  # pending, processing, completed, rejected
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("requested_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_dsar_requests_status", "dsar_requests", ["status"])


def downgrade():
    op.drop_index("ix_dsar_requests_status")
    op.drop_table("dsar_requests")
    op.drop_index("ix_consent_preferences_contact_id_unique")
    op.drop_table("consent_preferences")
    op.drop_column("emails", "deal_id")
