"""Phase 2: Lead scores table + contact intelligence columns.

Revision ID: 004_phase2
Revises: 003_perf
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "004_phase2"
down_revision = "003_perf"


def upgrade():
    # Lead scores table
    op.create_table(
        "lead_scores",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("contact_id", UUID(as_uuid=True), sa.ForeignKey("contacts.id"), nullable=False, index=True),
        sa.Column("fit_score", sa.Float, default=0),
        sa.Column("intent_score", sa.Float, default=0),
        sa.Column("instinct_score", sa.Float, default=0),
        sa.Column("composite_score", sa.Float, default=0),
        sa.Column("fit_breakdown", sa.Text, nullable=True),
        sa.Column("intent_breakdown", sa.Text, nullable=True),
        sa.Column("instinct_breakdown", sa.Text, nullable=True),
        sa.Column("calculated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_lead_scores_composite", "lead_scores", ["composite_score"])

    # New columns on contacts for intelligence
    op.add_column("contacts", sa.Column("channel_dna_json", sa.Text, nullable=True))
    op.add_column("contacts", sa.Column("trust_decay_status", sa.String(20), nullable=True))


def downgrade():
    op.drop_column("contacts", "trust_decay_status")
    op.drop_column("contacts", "channel_dna_json")
    op.drop_index("ix_lead_scores_composite")
    op.drop_table("lead_scores")
