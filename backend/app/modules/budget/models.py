import uuid
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.db.base import Base

Json = JSON().with_variant(JSONB(), "postgresql")


class BudgetStatus(StrEnum):
    DRAFT = "draft"
    PROCESSED = "processed"
    VALIDATED = "validated"
    CONFIRMED = "confirmed"
    REPLACED = "replaced"
    REJECTED = "rejected"
    CLOSED = "closed"


class CycleType(StrEnum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    MODIFIED = "modified"
    EXECUTED = "executed"
    CLOSED = "closed"


class Traceable:
    source_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("sources.id"))
    evidence_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("evidence.id"))
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", Json, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class BudgetCycle(Traceable, Base):
    __tablename__ = "budget_cycles"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    fiscal_year: Mapped[int] = mapped_column(Integer)
    jurisdiction: Mapped[str] = mapped_column(String(200))
    government_level: Mapped[str] = mapped_column(String(80))
    cycle_type: Mapped[CycleType] = mapped_column(Enum(CycleType))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    status: Mapped[BudgetStatus] = mapped_column(Enum(BudgetStatus))
    currency: Mapped[str] = mapped_column(String(3), default="DOP")
    legal_basis_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("legal_bases.id"))
    version: Mapped[int] = mapped_column(Integer, default=1)
    checksum: Mapped[str | None] = mapped_column(String(64))
    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    actor_type: Mapped[str] = mapped_column(String(30), default="human")


class BudgetClassifier(Traceable, Base):
    __tablename__ = "budget_classifiers"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    classifier_type: Mapped[str] = mapped_column(String(50))
    code: Mapped[str] = mapped_column(String(100))
    official_name: Mapped[str] = mapped_column(String(300))
    description: Mapped[str | None] = mapped_column(Text)
    hierarchy_level: Mapped[int] = mapped_column(Integer, default=0)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("budget_classifiers.id"))
    valid_from: Mapped[date] = mapped_column(Date)
    valid_to: Mapped[date | None] = mapped_column(Date)
    status: Mapped[BudgetStatus] = mapped_column(Enum(BudgetStatus))
    actor_type: Mapped[str] = mapped_column(String(30), default="human")


class FundingSource(Traceable, Base):
    __tablename__ = "funding_sources"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(100), unique=True)
    official_name: Mapped[str] = mapped_column(String(300))
    description: Mapped[str | None] = mapped_column(Text)
    valid_from: Mapped[date] = mapped_column(Date)
    valid_to: Mapped[date | None] = mapped_column(Date)
    status: Mapped[BudgetStatus] = mapped_column(Enum(BudgetStatus))
    actor_type: Mapped[str] = mapped_column(String(30), default="human")


class FinancingOrganization(Traceable, Base):
    __tablename__ = "financing_organizations"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(100), unique=True)
    official_name: Mapped[str] = mapped_column(String(300))
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[BudgetStatus] = mapped_column(Enum(BudgetStatus))
    actor_type: Mapped[str] = mapped_column(String(30), default="human")


class BudgetProgram(Traceable, Base):
    __tablename__ = "budget_programs"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    institution_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("institutions.id"))
    budget_cycle_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("budget_cycles.id"))
    parent_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("budget_programs.id"))
    program_code: Mapped[str] = mapped_column(String(100))
    official_name: Mapped[str] = mapped_column(String(300))
    normalized_name: Mapped[str] = mapped_column(String(300))
    program_type: Mapped[str] = mapped_column(String(40))
    territory_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("territories.id"))
    organizational_unit_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("organizational_units.id")
    )
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[BudgetStatus] = mapped_column(Enum(BudgetStatus))
    legal_basis_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("legal_bases.id"))
    actor_type: Mapped[str] = mapped_column(String(30), default="human")


class BudgetAppropriation(Traceable, Base):
    __tablename__ = "budget_appropriations"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    budget_cycle_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("budget_cycles.id"))
    institution_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("institutions.id"))
    program_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("budget_programs.id"))
    project_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("budget_programs.id"))
    activity_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("budget_programs.id"))
    organizational_unit_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("organizational_units.id")
    )
    territory_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("territories.id"))
    classifier_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("budget_classifiers.id"))
    funding_source_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("funding_sources.id"))
    financing_organization_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("financing_organizations.id")
    )
    approved_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    current_amount: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    currency: Mapped[str] = mapped_column(String(3))
    valid_from: Mapped[date] = mapped_column(Date)
    valid_to: Mapped[date | None] = mapped_column(Date)
    status: Mapped[BudgetStatus] = mapped_column(Enum(BudgetStatus))
    raw_payload: Mapped[dict[str, object]] = mapped_column(Json, default=dict)
    row_number: Mapped[int | None] = mapped_column(Integer)
    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    version: Mapped[int] = mapped_column(Integer, default=1)
    checksum: Mapped[str | None] = mapped_column(String(64))
    actor_type: Mapped[str] = mapped_column(String(30), default="human")


class BudgetModification(Traceable, Base):
    __tablename__ = "budget_modifications"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    budget_cycle_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("budget_cycles.id"))
    institution_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("institutions.id"))
    appropriation_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("budget_appropriations.id")
    )
    source_appropriation_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("budget_appropriations.id")
    )
    destination_appropriation_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("budget_appropriations.id")
    )
    modification_type: Mapped[str] = mapped_column(String(40))
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    previous_balance: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    resulting_balance: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    effective_date: Mapped[date] = mapped_column(Date)
    legal_reference: Mapped[str] = mapped_column(String(300))
    legal_basis_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("legal_bases.id"))
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[BudgetStatus] = mapped_column(Enum(BudgetStatus))
    actor_type: Mapped[str] = mapped_column(String(30), default="human")


class BudgetExecutionRecord(Traceable, Base):
    __tablename__ = "budget_execution_records"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    budget_cycle_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("budget_cycles.id"))
    institution_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("institutions.id"))
    appropriation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("budget_appropriations.id"))
    execution_period: Mapped[str] = mapped_column(String(30))
    period_start: Mapped[date] = mapped_column(Date)
    period_end: Mapped[date] = mapped_column(Date)
    initial_budget: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    current_budget: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    committed_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    accrued_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    paid_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    available_balance: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    currency: Mapped[str] = mapped_column(String(3))
    status: Mapped[BudgetStatus] = mapped_column(Enum(BudgetStatus))
    exception_documented: Mapped[bool] = mapped_column(default=False)
    row_number: Mapped[int | None] = mapped_column(Integer)
    raw_payload: Mapped[dict[str, object]] = mapped_column(Json, default=dict)
    reconciliation_flag: Mapped[bool] = mapped_column(default=False)
    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    version: Mapped[int] = mapped_column(Integer, default=1)
    checksum: Mapped[str | None] = mapped_column(String(64))
    actor_type: Mapped[str] = mapped_column(String(30), default="human")


class BudgetRevenue(Traceable, Base):
    __tablename__ = "budget_revenues"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    budget_cycle_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("budget_cycles.id"))
    institution_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("institutions.id"))
    revenue_classifier_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("budget_classifiers.id"))
    funding_source_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("funding_sources.id"))
    estimated_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    modified_estimate: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    collected_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    accrued_amount: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    period_start: Mapped[date] = mapped_column(Date)
    period_end: Mapped[date] = mapped_column(Date)
    currency: Mapped[str] = mapped_column(String(3))
    status: Mapped[BudgetStatus] = mapped_column(Enum(BudgetStatus))
    raw_payload: Mapped[dict[str, object]] = mapped_column(Json, default=dict)
    actor_type: Mapped[str] = mapped_column(String(30), default="human")


class InterinstitutionalTransfer(Traceable, Base):
    __tablename__ = "interinstitutional_transfers"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    budget_cycle_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("budget_cycles.id"))
    origin_institution_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("institutions.id"))
    destination_institution_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("institutions.id"))
    transfer_type: Mapped[str] = mapped_column(String(40))
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    paid_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    effective_date: Mapped[date] = mapped_column(Date)
    purpose: Mapped[str] = mapped_column(Text)
    legal_basis_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("legal_bases.id"))
    appropriation_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("budget_appropriations.id")
    )
    status: Mapped[BudgetStatus] = mapped_column(Enum(BudgetStatus))
    actor_type: Mapped[str] = mapped_column(String(30), default="human")


class BudgetVersion(Traceable, Base):
    __tablename__ = "budget_versions"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    entity_type: Mapped[str] = mapped_column(String(60))
    previous_entity_id: Mapped[uuid.UUID | None]
    new_entity_id: Mapped[uuid.UUID]
    action: Mapped[str] = mapped_column(String(30))
    reason: Mapped[str] = mapped_column(Text)
    effective_date: Mapped[date] = mapped_column(Date)
    actor: Mapped[str] = mapped_column(String(200))
    aggregate_differences: Mapped[dict[str, object]] = mapped_column(Json, default=dict)
    checksum: Mapped[str] = mapped_column(String(64))


class BudgetFinding(Base):
    __tablename__ = "budget_findings"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    finding_type: Mapped[str] = mapped_column(String(60))
    severity: Mapped[str] = mapped_column(String(30))
    institution_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("institutions.id"))
    budget_cycle_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("budget_cycles.id"))
    appropriation_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("budget_appropriations.id")
    )
    execution_record_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("budget_execution_records.id")
    )
    comparison_cycle_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("budget_cycles.id"))
    observed_value: Mapped[dict[str, object]] = mapped_column(Json, default=dict)
    expected_or_previous_value: Mapped[dict[str, object]] = mapped_column(Json, default=dict)
    explanation: Mapped[str] = mapped_column(Text)
    evidence_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("evidence.id"))
    status: Mapped[str] = mapped_column(String(30), default="open")
    reviewer_notes: Mapped[str | None] = mapped_column(Text)
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", Json, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
