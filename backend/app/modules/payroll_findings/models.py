import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.db.base import Base


class FindingSeverity(StrEnum):
    INFORMATIONAL = "informational"
    REVIEW_REQUIRED = "review_required"
    UNUSUAL = "unusual"
    HIGH_PRIORITY = "high_priority"


class FindingStatus(StrEnum):
    OPEN = "open"
    REVIEWED = "reviewed"
    DISMISSED = "dismissed"
    RESOLVED = "resolved"


class PayrollFinding(Base):
    __tablename__ = "payroll_findings"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    finding_type: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[FindingSeverity] = mapped_column(Enum(FindingSeverity), nullable=False)
    person_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("persons.id"))
    institution_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("institutions.id"), nullable=False)
    payroll_period_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("payroll_periods.id"), nullable=False
    )
    comparison_period_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("payroll_periods.id"))
    observed_value: Mapped[dict[str, object]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"), default=dict
    )
    expected_or_previous_value: Mapped[dict[str, object]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"), default=dict
    )
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("evidence.id"))
    status: Mapped[FindingStatus] = mapped_column(Enum(FindingStatus), default=FindingStatus.OPEN)
    reviewer_notes: Mapped[str | None] = mapped_column(Text)
    metadata_: Mapped[dict[str, object]] = mapped_column(
        "metadata", JSON().with_variant(JSONB(), "postgresql"), default=dict
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
