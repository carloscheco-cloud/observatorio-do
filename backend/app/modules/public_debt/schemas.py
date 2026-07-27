import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Currency = Field(default="DOP", pattern=r"^[A-Z]{3}$")
Money = Field(ge=0, max_digits=24, decimal_places=4)
Rate = Field(default=None, ge=0, le=1000, max_digits=12, decimal_places=8)


class TraceCreate(BaseModel):
    source_id: uuid.UUID
    evidence_id: uuid.UUID
    metadata_: dict[str, object] = Field(default_factory=dict)


class InstrumentCreate(TraceCreate):
    debtor_institution_id: uuid.UUID
    creditor_id: uuid.UUID | None = None
    instrument_code: str
    external_reference: str | None = None
    title: str
    description: str | None = None
    instrument_type: Literal[
        "loan",
        "sovereign_bond",
        "domestic_bond",
        "treasury_bill",
        "promissory_note",
        "supplier_credit",
        "lease_obligation",
        "public_private_partnership",
        "judgment_obligation",
        "accounts_payable",
        "other",
    ]
    debt_scope: Literal[
        "central_government",
        "decentralized_entity",
        "municipal",
        "public_enterprise",
        "guaranteed_debt",
        "consolidated_public_sector",
        "other",
    ]
    origin: Literal["domestic", "external", "other"]
    currency: str = Currency
    original_principal: Decimal = Money
    current_principal: Decimal = Money
    approved_amount: Decimal | None = Field(default=None, ge=0)
    signed_date: date | None = None
    effective_date: date
    maturity_date: date | None = None
    interest_type: Literal["fixed", "variable", "zero", "indexed", "mixed", "other"]
    nominal_interest_rate: Decimal | None = Rate
    reference_rate: Decimal | None = Rate
    spread_rate: Decimal | None = Rate
    grace_period_end: date | None = None
    payment_frequency: str | None = None
    status: str = "draft"
    legal_basis_id: uuid.UUID
    raw_payload: dict[str, object] = Field(default_factory=dict, exclude=True)
    row_location: str | None = None
    version: int = Field(default=1, ge=1)
    checksum: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    exception_documented: bool = False

    @model_validator(mode="after")
    def integrity(self) -> "InstrumentCreate":
        if self.maturity_date and self.maturity_date < self.effective_date:
            raise ValueError("maturity_date cannot precede effective_date")
        if self.current_principal > self.original_principal and not self.exception_documented:
            raise ValueError("current_principal cannot exceed original_principal")
        return self


class InstrumentRead(InstrumentCreate):
    id: uuid.UUID
    actor_type: str
    validation_status: str
    processed_at: datetime
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class DisbursementCreate(TraceCreate):
    debt_instrument_id: uuid.UUID
    debtor_institution_id: uuid.UUID
    disbursement_reference: str
    disbursement_date: date
    amount: Decimal = Field(gt=0)
    currency: str = Currency
    exchange_rate: Decimal | None = Field(default=None, gt=0)
    amount_local_currency: Decimal | None = Field(default=None, ge=0)
    destination_program_id: uuid.UUID | None = None
    destination_project_id: uuid.UUID | None = None
    budget_cycle_id: uuid.UUID | None = None
    budget_appropriation_id: uuid.UUID | None = None
    status: str = "confirmed"
    exception_documented: bool = False


class DisbursementRead(DisbursementCreate):
    id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class PaymentCreate(TraceCreate):
    debt_instrument_id: uuid.UUID
    schedule_id: uuid.UUID | None = None
    debtor_institution_id: uuid.UUID
    creditor_id: uuid.UUID | None = None
    payment_reference: str
    payment_date: date
    principal_paid: Decimal = Money
    interest_paid: Decimal = Money
    fees_paid: Decimal = Money
    penalties_paid: Decimal = Money
    total_paid: Decimal = Money
    currency: str = Currency
    exchange_rate: Decimal | None = Field(default=None, gt=0)
    amount_local_currency: Decimal | None = Field(default=None, ge=0)
    budget_execution_record_id: uuid.UUID | None = None
    status: str = "confirmed"
    exception_documented: bool = False

    @model_validator(mode="after")
    def total(self) -> "PaymentCreate":
        if self.total_paid != sum(
            (self.principal_paid, self.interest_paid, self.fees_paid, self.penalties_paid),
            Decimal(),
        ):
            raise ValueError("total_paid must equal payment components")
        return self


class PaymentRead(PaymentCreate):
    id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class GuaranteeCreate(TraceCreate):
    guarantor_institution_id: uuid.UUID
    beneficiary_creditor_id: uuid.UUID | None = None
    guaranteed_entity_id: uuid.UUID
    related_debt_instrument_id: uuid.UUID | None = None
    guarantee_code: str
    guarantee_type: str
    issue_date: date
    expiration_date: date | None = None
    guaranteed_amount: Decimal = Money
    outstanding_exposure: Decimal = Money
    currency: str = Currency
    probability_of_call: Decimal | None = Field(default=None, ge=0, le=1)
    status: str
    legal_basis_id: uuid.UUID
    exception_documented: bool = False

    @model_validator(mode="after")
    def integrity(self) -> "GuaranteeCreate":
        if (
            self.guarantor_institution_id == self.guaranteed_entity_id
            and not self.exception_documented
        ):
            raise ValueError("guarantor and guaranteed entity must differ")
        if self.outstanding_exposure > self.guaranteed_amount and not self.exception_documented:
            raise ValueError("exposure cannot exceed guaranteed amount")
        return self


class ObligationCreate(TraceCreate):
    institution_id: uuid.UUID
    creditor_id: uuid.UUID | None = None
    supplier_id: uuid.UUID | None = None
    obligation_code: str
    obligation_type: str
    description: str
    recognition_date: date
    due_date: date | None = None
    original_amount: Decimal = Money
    outstanding_amount: Decimal = Money
    paid_amount: Decimal = Money
    currency: str = Currency
    related_contract_id: uuid.UUID | None = None
    related_budget_execution_id: uuid.UUID | None = None
    status: str
    legal_basis_id: uuid.UUID | None = None

    @model_validator(mode="after")
    def amounts(self) -> "ObligationCreate":
        if self.outstanding_amount + self.paid_amount != self.original_amount:
            raise ValueError("outstanding_amount plus paid_amount must equal original_amount")
        return self


class TransferCreate(TraceCreate):
    origin_institution_id: uuid.UUID
    destination_institution_id: uuid.UUID
    budget_cycle_id: uuid.UUID | None = None
    transfer_code: str
    transfer_type: str
    approval_date: date
    payment_date: date | None = None
    approved_amount: Decimal = Money
    paid_amount: Decimal = Money
    currency: str = Currency
    purpose: str
    recurring: bool = False
    fiscal_year: int = Field(ge=1900, le=2200)
    status: str
    legal_basis_id: uuid.UUID
    exception_documented: bool = False

    @model_validator(mode="after")
    def integrity(self) -> "TransferCreate":
        if self.origin_institution_id == self.destination_institution_id:
            raise ValueError("origin and destination must differ")
        if self.paid_amount > self.approved_amount and not self.exception_documented:
            raise ValueError("paid_amount cannot exceed approved_amount")
        return self


class SubsidyCreate(TraceCreate):
    granting_institution_id: uuid.UUID
    beneficiary_institution_id: uuid.UUID | None = None
    beneficiary_supplier_id: uuid.UUID | None = None
    program_id: uuid.UUID | None = None
    subsidy_code: str
    subsidy_type: str
    period_start: date
    period_end: date
    approved_amount: Decimal = Money
    paid_amount: Decimal = Money
    currency: str = Currency
    purpose: str
    eligibility_basis: str | None = None
    status: str
    legal_basis_id: uuid.UUID


class CommitmentCreate(TraceCreate):
    institution_id: uuid.UUID
    commitment_code: str
    related_contract_id: uuid.UUID | None = None
    related_project_id: uuid.UUID | None = None
    start_year: int
    end_year: int
    total_committed_amount: Decimal = Money
    currency: str = Currency
    annual_breakdown: dict[str, Decimal]
    status: str
    legal_basis_id: uuid.UUID

    @model_validator(mode="after")
    def breakdown(self) -> "CommitmentCreate":
        if self.end_year < self.start_year:
            raise ValueError("end_year cannot precede start_year")
        if abs(
            sum(self.annual_breakdown.values(), Decimal()) - self.total_committed_amount
        ) > Decimal("0.01"):
            raise ValueError("annual breakdown must equal total commitment")
        return self


class GenericRead(BaseModel):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True, extra="allow")


class FindingReview(BaseModel):
    status: Literal["open", "reviewed", "dismissed", "confirmed_observation"]
    reviewer_notes: str | None = None


class DebtMetrics(BaseModel):
    institution_id: uuid.UUID
    instrument_count: int
    current_principal: Decimal
    principal_outstanding: Decimal
    accrued_interest: Decimal
    paid_service: Decimal
    projected_service: Decimal
    arrears: Decimal
    active_guarantees: Decimal
    pending_obligations: Decimal
