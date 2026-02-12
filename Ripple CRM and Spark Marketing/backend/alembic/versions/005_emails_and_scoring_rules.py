"""Phase 2b: Emails table, scoring_rules table, is_mql on lead_scores.

Revision ID: 005_emails
Revises: 004_phase2
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision = "005_emails"
down_revision = "004_phase2"


def upgrade():
    # Emails table
    op.create_table(
        "emails",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("contact_id", UUID(as_uuid=True), sa.ForeignKey("contacts.id"), nullable=True, index=True),
        sa.Column("direction", sa.String(10), nullable=False),
        sa.Column("subject", sa.String(500), nullable=True),
        sa.Column("body_text", sa.Text, nullable=True),
        sa.Column("body_html", sa.Text, nullable=True),
        sa.Column("from_address", sa.String(255), nullable=False),
        sa.Column("to_addresses", JSONB, nullable=True),
        sa.Column("cc_addresses", JSONB, nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("thread_id", sa.String(255), nullable=True, index=True),
        sa.Column("message_id", sa.String(255), nullable=True, unique=True),
        sa.Column("is_read", sa.Boolean, default=False),
        sa.Column("status", sa.String(20), default="synced"),
        sa.Column("metadata_json", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_emails_from_address", "emails", ["from_address"])
    op.create_index("ix_emails_sent_at", "emails", ["sent_at"])

    # Scoring rules table
    op.create_table(
        "scoring_rules",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("brain", sa.String(20), nullable=False),
        sa.Column("attribute", sa.String(100), nullable=False),
        sa.Column("label", sa.String(200), nullable=False),
        sa.Column("points", sa.Float, default=0),
        sa.Column("max_points", sa.Float, default=100),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("sort_order", sa.Integer, default=0),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_scoring_rules_brain", "scoring_rules", ["brain"])

    # Add is_mql to lead_scores
    op.add_column("lead_scores", sa.Column("is_mql", sa.Boolean, default=False))


def downgrade():
    op.drop_column("lead_scores", "is_mql")
    op.drop_index("ix_scoring_rules_brain")
    op.drop_table("scoring_rules")
    op.drop_index("ix_emails_sent_at")
    op.drop_index("ix_emails_from_address")
    op.drop_table("emails")
