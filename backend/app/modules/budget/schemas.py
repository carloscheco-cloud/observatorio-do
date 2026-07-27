import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.modules.budget.models import BudgetStatus, CycleType


class BudgetCycleCreate(BaseModel):
    fiscal_year: int = Field(ge=1900, le=2200)
    jurisdiction: str
    government_level: str
    cycle_type: CycleType
    start_date: date
    end_date: date
    status: BudgetStatus = BudgetStatus.DRAFT
    currency: str = Field(default="DOP", pattern=r"^[A-Z]{3}$")
    legal_basis_id: uuid.UUID | None = None
    source_id: uuid.UUID | None = None
    evidence_id: uuid.UUID | None = None
    version: int = Field(default=1, ge=1)
    checksum: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    metadata_: dict[str, object] = Field(default_factory=dict)

    @model_validator(mode="after")
    def integrity(self) -> "BudgetCycleCreate":
        if self.end_date < self.start_date:
            raise ValueError("end_date must not precede start_date")
        if self.status == BudgetStatus.CONFIRMED and not all(
            (self.source_id, self.evidence_id, self.legal_basis_id)
        ):
            raise ValueError("Confirmed cycle requires source, evidence and legal basis")
        return self


class BudgetCycleRead(BudgetCycleCreate):
    id: uuid.UUID
    actor_type: str
    processed_at: datetime
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ClassifierCreate(BaseModel):
    classifier_type: Literal[
        "institutional",
        "functional",
        "economic",
        "object_of_expenditure",
        "geographic",
        "source_of_funds",
        "programmatic",
        "revenue",
        "expenditure",
    ]
    code: str
    official_name: str
    description: str | None = None
    hierarchy_level: int = Field(default=0, ge=0)
    parent_id: uuid.UUID | None = None
    valid_from: date
    valid_to: date | None = None
    status: BudgetStatus = BudgetStatus.DRAFT
    source_id: uuid.UUID | None = None
    evidence_id: uuid.UUID | None = None
    metadata_: dict[str, object] = Field(default_factory=dict)


class ClassifierRead(ClassifierCreate):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ProgramCreate(BaseModel):
    institution_id: uuid.UUID
    budget_cycle_id: uuid.UUID
    parent_id: uuid.UUID | None = None
    program_code: str
    official_name: str
    normalized_name: str
    program_type: Literal["program", "subprogram", "project", "activity", "work", "product"]
    territory_id: uuid.UUID | None = None
    organizational_unit_id: uuid.UUID | None = None
    start_date: date
    end_date: date | None = None
    status: BudgetStatus = BudgetStatus.DRAFT
    legal_basis_id: uuid.UUID | None = None
    source_id: uuid.UUID | None = None
    evidence_id: uuid.UUID | None = None
    metadata_: dict[str, object] = Field(default_factory=dict)


class ProgramRead(ProgramCreate):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AppropriationCreate(BaseModel):
    budget_cycle_id: uuid.UUID
    institution_id: uuid.UUID
    program_id: uuid.UUID | None = None
    project_id: uuid.UUID | None = None
    activity_id: uuid.UUID | None = None
    organizational_unit_id: uuid.UUID | None = None
    territory_id: uuid.UUID | None = None
    classifier_id: uuid.UUID
    funding_source_id: uuid.UUID | None = None
    financing_organization_id: uuid.UUID | None = None
    approved_amount: Decimal = Field(ge=0)
    current_amount: Decimal | None = Field(default=None, ge=0)
    currency: str = Field(default="DOP", pattern=r"^[A-Z]{3}$")
    valid_from: date
    valid_to: date | None = None
    status: BudgetStatus = BudgetStatus.DRAFT
    source_id: uuid.UUID | None = None
    evidence_id: uuid.UUID | None = None
    row_number: int | None = Field(default=None, ge=1)
    version: int = Field(default=1, ge=1)
    checksum: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    raw_payload: dict[str, object] = Field(default_factory=dict)
    metadata_: dict[str, object] = Field(default_factory=dict)

    @model_validator(mode="after")
    def traceability(self) -> "AppropriationCreate":
        if self.status == BudgetStatus.CONFIRMED and (
            self.current_amount is None or self.source_id is None or self.evidence_id is None
        ):
            raise ValueError("Confirmed appropriation requires amount, source and evidence")
        return self


class AppropriationRead(AppropriationCreate):
    id: uuid.UUID
    actor_type: str
    processed_at: datetime
    created_at: datetime
    updated_at: datetime
    raw_payload: dict[str, object] = Field(exclude=True)
    model_config = ConfigDict(from_attributes=True)


class ModificationCreate(BaseModel):
    budget_cycle_id: uuid.UUID
    institution_id: uuid.UUID
    appropriation_id: uuid.UUID | None = None
    source_appropriation_id: uuid.UUID | None = None
    destination_appropriation_id: uuid.UUID | None = None
    modification_type: str
    amount: Decimal = Field(gt=0)
    previous_balance: Decimal = Field(ge=0)
    resulting_balance: Decimal = Field(ge=0)
    effective_date: date
    legal_reference: str
    legal_basis_id: uuid.UUID | None = None
    source_id: uuid.UUID | None = None
    evidence_id: uuid.UUID | None = None
    description: str
    status: BudgetStatus = BudgetStatus.DRAFT
    metadata_: dict[str, object] = Field(default_factory=dict)


class ModificationRead(ModificationCreate):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ExecutionCreate(BaseModel):
    budget_cycle_id: uuid.UUID
    institution_id: uuid.UUID
    appropriation_id: uuid.UUID
    execution_period: str
    period_start: date
    period_end: date
    initial_budget: Decimal = Field(ge=0)
    current_budget: Decimal = Field(ge=0)
    committed_amount: Decimal = Field(ge=0)
    accrued_amount: Decimal = Field(ge=0)
    paid_amount: Decimal = Field(ge=0)
    available_balance: Decimal = Field(ge=0)
    currency: str = Field(default="DOP", pattern=r"^[A-Z]{3}$")
    status: BudgetStatus = BudgetStatus.DRAFT
    source_id: uuid.UUID | None = None
    evidence_id: uuid.UUID | None = None
    exception_documented: bool = False
    row_number: int | None = None
    raw_payload: dict[str, object] = Field(default_factory=dict)
    metadata_: dict[str, object] = Field(default_factory=dict)

    @model_validator(mode="after")
    def integrity(self) -> "ExecutionCreate":
        if self.period_end < self.period_start:
            raise ValueError("Invalid execution period")
        if not self.exception_documented and not (
            self.paid_amount <= self.accrued_amount <= self.committed_amount
        ):
            raise ValueError("Paid/accrued/committed amounts are inconsistent")
        if self.status == BudgetStatus.CONFIRMED and not (self.source_id and self.evidence_id):
            raise ValueError("Confirmed execution requires source and evidence")
        return self


class ExecutionRead(ExecutionCreate):
    id: uuid.UUID
    reconciliation_flag: bool
    processed_at: datetime
    created_at: datetime
    updated_at: datetime
    raw_payload: dict[str, object] = Field(exclude=True)
    model_config = ConfigDict(from_attributes=True)


class BudgetMetrics(BaseModel):
    approved: Decimal
    current: Decimal
    committed: Decimal
    accrued: Decimal
    paid: Decimal
    available: Decimal
    execution_percentage: Decimal
    net_modifications: Decimal


class FindingReview(BaseModel):
    status: Literal["open", "reviewed", "dismissed", "resolved"]
    reviewer_notes: str | None = None


class RevenueCreate(BaseModel):
    budget_cycle_id: uuid.UUID
    institution_id: uuid.UUID | None = None
    revenue_classifier_id: uuid.UUID
    funding_source_id: uuid.UUID | None = None
    estimated_amount: Decimal = Field(ge=0)
    modified_estimate: Decimal = Field(ge=0)
    collected_amount: Decimal = Field(ge=0)
    accrued_amount: Decimal | None = Field(default=None, ge=0)
    period_start: date
    period_end: date
    currency: str = Field(default="DOP", pattern=r"^[A-Z]{3}$")
    status: BudgetStatus = BudgetStatus.DRAFT
    source_id: uuid.UUID | None = None
    evidence_id: uuid.UUID | None = None
    raw_payload: dict[str, object] = Field(default_factory=dict)
    metadata_: dict[str, object] = Field(default_factory=dict)


class RevenueRead(RevenueCreate):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    raw_payload: dict[str, object] = Field(exclude=True)
    model_config = ConfigDict(from_attributes=True)


class TransferCreate(BaseModel):
    budget_cycle_id: uuid.UUID
    origin_institution_id: uuid.UUID
    destination_institution_id: uuid.UUID
    transfer_type: Literal[
        "current_transfer",
        "capital_transfer",
        "subsidy",
        "grant",
        "contribution",
        "shared_revenue",
        "other",
    ]
    amount: Decimal = Field(gt=0)
    paid_amount: Decimal = Field(default=Decimal(0), ge=0)
    effective_date: date
    purpose: str
    legal_basis_id: uuid.UUID
    appropriation_id: uuid.UUID | None = None
    source_id: uuid.UUID
    evidence_id: uuid.UUID
    status: BudgetStatus = BudgetStatus.DRAFT
    metadata_: dict[str, object] = Field(default_factory=dict)

    @model_validator(mode="after")
    def distinct_institutions(self) -> "TransferCreate":
        if self.origin_institution_id == self.destination_institution_id:
            raise ValueError("Origin and destination must differ")
        return self


class TransferRead(TransferCreate):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
