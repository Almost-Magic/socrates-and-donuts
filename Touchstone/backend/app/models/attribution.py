"""Touchstone — Attribution model (Phase 2 calculations, schema created now)."""

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import String, DateTime, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Attribution(Base):
    __tablename__ = "touchstone_attributions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("touchstone_deals.id"), index=True
    )
    touchpoint_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("touchstone_touchpoints.id")
    )
    campaign_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("touchstone_campaigns.id")
    )
    model: Mapped[str] = mapped_column(String(50))
    attributed_amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    attribution_weight: Mapped[Decimal | None] = mapped_column(Numeric(5, 4))
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
