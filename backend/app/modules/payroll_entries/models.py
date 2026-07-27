import uuid
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.db.base import Base


class PayrollEntryStatus(StrEnum):
    DRAFT = "draft"
    NORMALIZED = "normalized"
    VALIDATED = "validated"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


class ComponentKind(StrEnum):
    INCOME = "income"
    DEDUCTION = "deduction"


class PayrollConceptCode(StrEnum):
    BASE_SALARY = "base_salary"
    REPRESENTATION_EXPENSE = "representation_expense"
    INCENTIVE = "incentive"
    BONUS = "bonus"
    OVERTIME = "overtime"
    PER_DIEM = "per_diem"
    ALLOWANCE = "allowance"
    COMMISSION = "commission"
    RETROACTIVE_PAYMENT = "retroactive_payment"
    SEVERANCE = "severance"
    SOCIAL_SECURITY = "social_security"
    PENSION = "pension"
    INCOME_TAX = "income_tax"
    HEALTH_INSURANCE = "health_insurance"
    LOAN_DEDUCTION = "loan_deduction"
    OTHER_INCOME = "other_income"
    OTHER_DEDUCTION = "other_deduction"


class PayrollEntry(Base):
    __tablename__ = "payroll_entries"
    __table_args__ = (
        UniqueConstraint(
            "payroll_period_id",
            "person_id",
            "position_id",
            "organizational_unit_id",
            name="uq_payroll_entry_canonical",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    payroll_period_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("payroll_periods.id"), nullable=False
    )
    employment_relationship_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("employment_relationships.id")
    )
    person_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("persons.id"), nullable=False)
    institution_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("institutions.id"), nullable=False)
    position_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("positions.id"))
    organizational_unit_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("organizational_units.id")
    )
    employee_reference_hash: Mapped[str | None] = mapped_column(String(64))
    listed_name: Mapped[str] = mapped_column(String(300), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(300), nullable=False)
    employment_type: Mapped[str | None] = mapped_column(String(50))
    base_salary: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    gross_income: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    total_deductions: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    net_income: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    other_compensation: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    status: Mapped[PayrollEntryStatus] = mapped_column(Enum(PayrollEntryStatus), nullable=False)
    source_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("sources.id"))
    evidence_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("evidence.id"))
    row_number: Mapped[int | None] = mapped_column(Integer)
    reconciliation_flag: Mapped[bool] = mapped_column(default=False, nullable=False)
    raw_payload: Mapped[dict[str, object]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"), default=dict, nullable=False
    )
    metadata_: Mapped[dict[str, object]] = mapped_column(
        "metadata", JSON().with_variant(JSONB(), "postgresql"), default=dict, nullable=False
    )
    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    actor_type: Mapped[str] = mapped_column(String(30), default="human", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PayrollConcept(Base):
    __tablename__ = "payroll_concepts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    code: Mapped[PayrollConceptCode] = mapped_column(Enum(PayrollConceptCode), unique=True)
    kind: Mapped[ComponentKind] = mapped_column(Enum(ComponentKind), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    metadata_: Mapped[dict[str, object]] = mapped_column(
        "metadata", JSON().with_variant(JSONB(), "postgresql"), default=dict
    )


class PayrollEntryComponent(Base):
    __tablename__ = "payroll_entry_components"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    payroll_entry_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("payroll_entries.id"), nullable=False
    )
    concept_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("payroll_concepts.id"), nullable=False)
    kind: Mapped[ComponentKind] = mapped_column(Enum(ComponentKind), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sources.id"), nullable=False)
    evidence_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("evidence.id"), nullable=False)
    metadata_: Mapped[dict[str, object]] = mapped_column(
        "metadata", JSON().with_variant(JSONB(), "postgresql"), default=dict
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
