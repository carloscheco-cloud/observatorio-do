import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.modules.procurement_processes.models import (
    ProcedureType,
    ProcessStatus,
    ProcurementType,
)

Currency = Field(default="DOP", pattern=r"^[A-Z]{3}$")


class ProcessCreate(BaseModel):
    institution_id: uuid.UUID
    organizational_unit_id: uuid.UUID | None = None
    procurement_unit_name: str | None = None
    process_code: str
    external_reference: str | None = None
    title: str
    description: str | None = None
    procurement_type: ProcurementType
    procedure_type: ProcedureType
    process_status: ProcessStatus = ProcessStatus.DRAFT
    publication_date: datetime | None = None
    submission_deadline: datetime | None = None
    opening_date: datetime | None = None
    award_date: date | None = None
    estimated_amount: Decimal = Field(ge=0)
    currency: str = Currency
    fiscal_year: int = Field(ge=1900, le=2200)
    territory_id: uuid.UUID | None = None
    budget_cycle_id: uuid.UUID | None = None
    budget_appropriation_id: uuid.UUID | None = None
    legal_basis_id: uuid.UUID | None = None
    source_id: uuid.UUID
    evidence_id: uuid.UUID
    raw_payload: dict[str, object] = Field(default_factory=dict, exclude=True)
    metadata_: dict[str, object] = Field(default_factory=dict)
    row_location: str | None = None
    version: int = Field(default=1, ge=1)
    checksum: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def dates(self) -> "ProcessCreate":
        timeline = [self.publication_date, self.submission_deadline, self.opening_date]
        present = [item for item in timeline if item is not None]
        if present != sorted(present):
            raise ValueError("Process dates must be chronological")
        if self.award_date and self.opening_date and self.award_date < self.opening_date.date():
            raise ValueError("award_date must not precede opening_date")
        return self


class ProcessRead(ProcessCreate):
    id: uuid.UUID
    actor_type: str
    validation_status: str
    processed_at: datetime
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class LotCreate(BaseModel):
    procurement_process_id: uuid.UUID
    lot_number: str
    title: str
    description: str
    estimated_amount: Decimal = Field(ge=0)
    awarded_amount: Decimal | None = Field(default=None, ge=0)
    currency: str = Currency
    status: str
    multiple_awards: bool = False
    source_id: uuid.UUID
    evidence_id: uuid.UUID
    metadata_: dict[str, object] = Field(default_factory=dict)


class LotRead(LotCreate):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)


class ItemCreate(BaseModel):
    procurement_process_id: uuid.UUID
    lot_id: uuid.UUID | None = None
    item_code: str | None = None
    classification_code: str | None = None
    description: str
    quantity: Decimal = Field(ge=0)
    unit_of_measure: str
    estimated_unit_price: Decimal | None = Field(default=None, ge=0)
    awarded_unit_price: Decimal | None = Field(default=None, ge=0)
    estimated_total: Decimal = Field(ge=0)
    awarded_total: Decimal | None = Field(default=None, ge=0)
    currency: str = Currency
    source_id: uuid.UUID
    evidence_id: uuid.UUID
    metadata_: dict[str, object] = Field(default_factory=dict)


class ItemRead(ItemCreate):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)


class BidCreate(BaseModel):
    procurement_process_id: uuid.UUID
    lot_id: uuid.UUID | None = None
    supplier_id: uuid.UUID
    submission_date: datetime
    offered_amount: Decimal = Field(ge=0)
    currency: str = Currency
    bid_status: Literal[
        "submitted",
        "admitted",
        "rejected",
        "withdrawn",
        "evaluated",
        "selected",
        "not_selected",
        "disqualified",
    ]
    technical_score: Decimal | None = Field(default=None, ge=0, le=100)
    financial_score: Decimal | None = Field(default=None, ge=0, le=100)
    total_score: Decimal | None = Field(default=None, ge=0, le=100)
    is_compliant: bool | None = None
    rejection_reason: str | None = None
    source_id: uuid.UUID
    evidence_id: uuid.UUID
    metadata_: dict[str, object] = Field(default_factory=dict)


class BidRead(BidCreate):
    id: uuid.UUID
    actor_type: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AwardCreate(BaseModel):
    procurement_process_id: uuid.UUID
    lot_id: uuid.UUID | None = None
    supplier_id: uuid.UUID
    bid_id: uuid.UUID | None = None
    award_reference: str
    award_date: date
    awarded_amount: Decimal = Field(ge=0)
    currency: str = Currency
    award_status: Literal[
        "proposed",
        "confirmed",
        "revoked",
        "cancelled",
        "appealed",
        "replaced",
        "partially_executed",
        "completed",
    ]
    legal_basis_id: uuid.UUID | None = None
    source_id: uuid.UUID
    evidence_id: uuid.UUID
    metadata_: dict[str, object] = Field(default_factory=dict)


class AwardRead(AwardCreate):
    id: uuid.UUID
    actor_type: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ContractCreate(BaseModel):
    procurement_process_id: uuid.UUID
    award_id: uuid.UUID
    institution_id: uuid.UUID
    supplier_id: uuid.UUID
    contract_code: str
    title: str
    description: str | None = None
    signature_date: date
    start_date: date
    end_date: date
    original_amount: Decimal = Field(ge=0)
    current_amount: Decimal = Field(ge=0)
    paid_amount: Decimal = Field(default=Decimal("0"), ge=0)
    currency: str = Currency
    contract_status: Literal[
        "draft",
        "signed",
        "active",
        "suspended",
        "completed",
        "terminated",
        "cancelled",
        "expired",
        "under_review",
        "replaced",
    ]
    procurement_type: ProcurementType
    territory_id: uuid.UUID | None = None
    organizational_unit_id: uuid.UUID | None = None
    budget_cycle_id: uuid.UUID | None = None
    budget_appropriation_id: uuid.UUID | None = None
    legal_basis_id: uuid.UUID | None = None
    source_id: uuid.UUID
    evidence_id: uuid.UUID
    raw_payload: dict[str, object] = Field(default_factory=dict, exclude=True)
    metadata_: dict[str, object] = Field(default_factory=dict)
    exception_documented: bool = False
    version: int = Field(default=1, ge=1)
    checksum: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def integrity(self) -> "ContractCreate":
        if not self.signature_date <= self.start_date <= self.end_date:
            raise ValueError("Contract dates must be chronological")
        if self.paid_amount > self.current_amount and not self.exception_documented:
            raise ValueError("paid_amount cannot exceed current_amount")
        return self


class ContractRead(ContractCreate):
    id: uuid.UUID
    actor_type: str
    processed_at: datetime
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AmendmentCreate(BaseModel):
    contract_id: uuid.UUID
    amendment_number: str
    amendment_type: Literal[
        "amount_increase",
        "amount_decrease",
        "extension",
        "reduction_of_term",
        "scope_change",
        "supplier_change",
        "suspension",
        "restart",
        "correction",
        "termination",
        "other",
    ]
    effective_date: date
    previous_amount: Decimal = Field(ge=0)
    new_amount: Decimal = Field(ge=0)
    previous_end_date: date | None = None
    new_end_date: date | None = None
    description: str
    legal_basis_id: uuid.UUID
    source_id: uuid.UUID
    evidence_id: uuid.UUID
    status: str
    metadata_: dict[str, object] = Field(default_factory=dict)


class AmendmentRead(AmendmentCreate):
    id: uuid.UUID
    actor_type: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class PaymentCreate(BaseModel):
    contract_id: uuid.UUID
    institution_id: uuid.UUID
    supplier_id: uuid.UUID
    payment_reference: str
    payment_date: date
    gross_amount: Decimal = Field(ge=0)
    deductions: Decimal = Field(ge=0)
    net_amount: Decimal = Field(ge=0)
    currency: str = Currency
    budget_execution_record_id: uuid.UUID | None = None
    status: str
    source_id: uuid.UUID
    evidence_id: uuid.UUID
    exception_documented: bool = False
    metadata_: dict[str, object] = Field(default_factory=dict)

    @model_validator(mode="after")
    def amount(self) -> "PaymentCreate":
        if self.net_amount != self.gross_amount - self.deductions:
            raise ValueError("net_amount must equal gross_amount minus deductions")
        return self


class PaymentRead(PaymentCreate):
    id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class FindingRead(BaseModel):
    id: uuid.UUID
    finding_type: str
    severity: str
    institution_id: uuid.UUID
    procurement_process_id: uuid.UUID | None
    contract_id: uuid.UUID | None
    supplier_id: uuid.UUID | None
    observed_value: dict[str, object]
    expected_or_previous_value: dict[str, object] | None
    explanation: str
    evidence_id: uuid.UUID
    status: str
    reviewer_notes: str | None
    metadata_: dict[str, object]
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class FindingReview(BaseModel):
    status: Literal["open", "reviewed", "dismissed", "confirmed_observation"]
    reviewer_notes: str | None = None


class ProcurementMetrics(BaseModel):
    process_count: int
    estimated_amount: Decimal
    awarded_amount: Decimal
    contracted_amount: Decimal
    modified_amount: Decimal
    paid_amount: Decimal
    estimated_award_difference: Decimal
    average_competition: Decimal
    single_bidder_processes: int
    expired_contracts: int
    execution_percentage: Decimal
