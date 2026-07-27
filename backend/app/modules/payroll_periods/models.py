import uuid
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import (
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.db.base import Base


class PayrollPeriodStatus(StrEnum):
    DRAFT = "draft"
    PROCESSED = "processed"
    VALIDATED = "validated"
    CONFIRMED = "confirmed"
    REPLACED = "replaced"
    REJECTED = "rejected"


class PayrollVersionAction(StrEnum):
    INITIAL = "initial"
    CORRECTION = "correction"
    REPLACEMENT = "replacement"
    CANCELLATION = "cancellation"
    REPUBLICATION = "republication"


class PayrollPeriod(Base):
    __tablename__ = "payroll_periods"
    __table_args__ = (
        UniqueConstraint(
            "institution_id", "year", "month", "version", name="uq_payroll_period_version"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    institution_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("institutions.id"), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    publication_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[PayrollPeriodStatus] = mapped_column(Enum(PayrollPeriodStatus), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="DOP", nullable=False)
    source_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("sources.id"))
    evidence_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("evidence.id"))
    record_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reported_gross_total: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    calculated_gross_total: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    calculated_net_total: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    checksum: Mapped[str | None] = mapped_column(String(64))
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    actor_type: Mapped[str] = mapped_column(String(30), default="human", nullable=False)
    metadata_: Mapped[dict[str, object]] = mapped_column(
        "metadata", JSON().with_variant(JSONB(), "postgresql"), default=dict, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class PayrollVersion(Base):
    __tablename__ = "payroll_versions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    previous_period_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("payroll_periods.id"))
    new_period_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("payroll_periods.id"), nullable=False
    )
    action: Mapped[PayrollVersionAction] = mapped_column(Enum(PayrollVersionAction), nullable=False)
    reason: Mapped[str] = mapped_column(String(1000), nullable=False)
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sources.id"), nullable=False)
    evidence_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("evidence.id"), nullable=False)
    aggregate_differences: Mapped[dict[str, object]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"), default=dict, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
