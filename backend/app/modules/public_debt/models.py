import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.db.base import Base

Json = JSON().with_variant(JSONB(), "postgresql")
Money = Numeric(24, 4)
Rate = Numeric(12, 8)


class Traceable:
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sources.id"))
    evidence_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("evidence.id"))
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", Json, default=dict)


class Audited:
    actor_type: Mapped[str] = mapped_column(String(30), default="human")
    validation_status: Mapped[str] = mapped_column(String(30), default="confirmed")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DebtInstrument(Traceable, Audited, Base):
    __tablename__ = "debt_instruments"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    debtor_institution_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("institutions.id"), index=True
    )
    creditor_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("creditors.id"), index=True)
    instrument_code: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    external_reference: Mapped[str | None] = mapped_column(String(300))
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text)
    instrument_type: Mapped[str] = mapped_column(String(40))
    debt_scope: Mapped[str] = mapped_column(String(40))
    origin: Mapped[str] = mapped_column(String(20))
    currency: Mapped[str] = mapped_column(String(3), index=True)
    original_principal: Mapped[Decimal] = mapped_column(Money)
    current_principal: Mapped[Decimal] = mapped_column(Money)
    approved_amount: Mapped[Decimal | None] = mapped_column(Money)
    signed_date: Mapped[date | None] = mapped_column(Date)
    effective_date: Mapped[date] = mapped_column(Date, index=True)
    maturity_date: Mapped[date | None] = mapped_column(Date, index=True)
    interest_type: Mapped[str] = mapped_column(String(20))
    nominal_interest_rate: Mapped[Decimal | None] = mapped_column(Rate)
    reference_rate: Mapped[Decimal | None] = mapped_column(Rate)
    spread_rate: Mapped[Decimal | None] = mapped_column(Rate)
    grace_period_end: Mapped[date | None] = mapped_column(Date)
    payment_frequency: Mapped[str | None] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(30), index=True)
    legal_basis_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("legal_bases.id"))
    raw_payload: Mapped[dict[str, object]] = mapped_column(Json, default=dict)
    row_location: Mapped[str | None] = mapped_column(String(300))
    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    version: Mapped[int] = mapped_column(Integer, default=1)
    checksum: Mapped[str | None] = mapped_column(String(64), index=True)
    exception_documented: Mapped[bool] = mapped_column(Boolean, default=False)


class DebtTerm(Traceable, Base):
    __tablename__ = "debt_terms"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    debt_instrument_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("debt_instruments.id"), index=True
    )
    valid_from: Mapped[date] = mapped_column(Date)
    valid_to: Mapped[date | None] = mapped_column(Date)
    interest_type: Mapped[str] = mapped_column(String(20))
    nominal_rate: Mapped[Decimal | None] = mapped_column(Rate)
    reference_rate_name: Mapped[str | None] = mapped_column(String(100))
    reference_rate_value: Mapped[Decimal | None] = mapped_column(Rate)
    spread_rate: Mapped[Decimal | None] = mapped_column(Rate)
    penalty_rate: Mapped[Decimal | None] = mapped_column(Rate)
    payment_frequency: Mapped[str] = mapped_column(String(30))
    amortization_method: Mapped[str | None] = mapped_column(String(50))
    grace_period_end: Mapped[date | None] = mapped_column(Date)
    day_count_convention: Mapped[str | None] = mapped_column(String(30))
    currency: Mapped[str] = mapped_column(String(3))


class DebtDisbursement(Traceable, Base):
    __tablename__ = "debt_disbursements"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    debt_instrument_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("debt_instruments.id"), index=True
    )
    debtor_institution_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("institutions.id"), index=True
    )
    disbursement_reference: Mapped[str] = mapped_column(String(150))
    disbursement_date: Mapped[date] = mapped_column(Date)
    amount: Mapped[Decimal] = mapped_column(Money)
    currency: Mapped[str] = mapped_column(String(3))
    exchange_rate: Mapped[Decimal | None] = mapped_column(Rate)
    amount_local_currency: Mapped[Decimal | None] = mapped_column(Money)
    destination_program_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("budget_programs.id")
    )
    destination_project_id: Mapped[uuid.UUID | None]
    budget_cycle_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("budget_cycles.id"))
    budget_appropriation_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("budget_appropriations.id")
    )
    status: Mapped[str] = mapped_column(String(30), index=True)
    exception_documented: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DebtServiceSchedule(Traceable, Audited, Base):
    __tablename__ = "debt_service_schedules"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    debt_instrument_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("debt_instruments.id"), index=True
    )
    installment_number: Mapped[int] = mapped_column(Integer)
    due_date: Mapped[date] = mapped_column(Date, index=True)
    principal_due: Mapped[Decimal] = mapped_column(Money)
    interest_due: Mapped[Decimal] = mapped_column(Money)
    fees_due: Mapped[Decimal] = mapped_column(Money)
    penalties_due: Mapped[Decimal] = mapped_column(Money)
    total_due: Mapped[Decimal] = mapped_column(Money)
    currency: Mapped[str] = mapped_column(String(3))
    schedule_status: Mapped[str] = mapped_column(String(30), index=True)


class DebtPayment(Traceable, Base):
    __tablename__ = "debt_payments"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    debt_instrument_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("debt_instruments.id"), index=True
    )
    schedule_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("debt_service_schedules.id"))
    debtor_institution_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("institutions.id"), index=True
    )
    creditor_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("creditors.id"), index=True)
    payment_reference: Mapped[str] = mapped_column(String(150))
    payment_date: Mapped[date] = mapped_column(Date, index=True)
    principal_paid: Mapped[Decimal] = mapped_column(Money)
    interest_paid: Mapped[Decimal] = mapped_column(Money)
    fees_paid: Mapped[Decimal] = mapped_column(Money)
    penalties_paid: Mapped[Decimal] = mapped_column(Money)
    total_paid: Mapped[Decimal] = mapped_column(Money)
    currency: Mapped[str] = mapped_column(String(3))
    exchange_rate: Mapped[Decimal | None] = mapped_column(Rate)
    amount_local_currency: Mapped[Decimal | None] = mapped_column(Money)
    budget_execution_record_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("budget_execution_records.id")
    )
    status: Mapped[str] = mapped_column(String(30), index=True)
    exception_documented: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DebtBalanceSnapshot(Traceable, Base):
    __tablename__ = "debt_balance_snapshots"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    debt_instrument_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("debt_instruments.id"), index=True
    )
    snapshot_date: Mapped[date] = mapped_column(Date, index=True)
    principal_outstanding: Mapped[Decimal] = mapped_column(Money)
    interest_accrued: Mapped[Decimal] = mapped_column(Money)
    arrears_principal: Mapped[Decimal] = mapped_column(Money)
    arrears_interest: Mapped[Decimal] = mapped_column(Money)
    fees_outstanding: Mapped[Decimal] = mapped_column(Money)
    total_outstanding: Mapped[Decimal] = mapped_column(Money)
    currency: Mapped[str] = mapped_column(String(3))
    exchange_rate: Mapped[Decimal | None] = mapped_column(Rate)
    total_local_currency: Mapped[Decimal | None] = mapped_column(Money)
    valuation_method: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(30), index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    checksum: Mapped[str | None] = mapped_column(String(64), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DebtIssuance(Traceable, Audited, Base):
    __tablename__ = "debt_issuances"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    debt_instrument_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("debt_instruments.id"), index=True
    )
    issuance_code: Mapped[str] = mapped_column(String(150), unique=True)
    issue_date: Mapped[date] = mapped_column(Date)
    settlement_date: Mapped[date | None] = mapped_column(Date)
    maturity_date: Mapped[date] = mapped_column(Date)
    face_value: Mapped[Decimal] = mapped_column(Money)
    issued_amount: Mapped[Decimal] = mapped_column(Money)
    coupon_rate: Mapped[Decimal | None] = mapped_column(Rate)
    yield_rate: Mapped[Decimal | None] = mapped_column(Rate)
    issue_price: Mapped[Decimal | None] = mapped_column(Rate)
    currency: Mapped[str] = mapped_column(String(3))
    market_type: Mapped[str] = mapped_column(String(30))
    placement_method: Mapped[str] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(30))
    legal_basis_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("legal_bases.id"))


class PublicGuarantee(Traceable, Audited, Base):
    __tablename__ = "public_guarantees"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    guarantor_institution_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("institutions.id"), index=True
    )
    beneficiary_creditor_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("creditors.id"), index=True
    )
    guaranteed_entity_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("institutions.id"))
    related_debt_instrument_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("debt_instruments.id")
    )
    guarantee_code: Mapped[str] = mapped_column(String(150), unique=True)
    guarantee_type: Mapped[str] = mapped_column(String(40))
    issue_date: Mapped[date] = mapped_column(Date)
    expiration_date: Mapped[date | None] = mapped_column(Date)
    guaranteed_amount: Mapped[Decimal] = mapped_column(Money)
    outstanding_exposure: Mapped[Decimal] = mapped_column(Money)
    currency: Mapped[str] = mapped_column(String(3))
    probability_of_call: Mapped[Decimal | None] = mapped_column(Rate)
    status: Mapped[str] = mapped_column(String(30), index=True)
    legal_basis_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("legal_bases.id"))
    exception_documented: Mapped[bool] = mapped_column(Boolean, default=False)


class GuaranteeEvent(Traceable, Base):
    __tablename__ = "guarantee_events"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    guarantee_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("public_guarantees.id"), index=True)
    event_type: Mapped[str] = mapped_column(String(30))
    event_date: Mapped[date] = mapped_column(Date)
    amount: Mapped[Decimal] = mapped_column(Money)
    currency: Mapped[str] = mapped_column(String(3))
    description: Mapped[str] = mapped_column(Text)
    related_debt_instrument_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("debt_instruments.id")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PublicObligation(Traceable, Audited, Base):
    __tablename__ = "public_obligations"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    institution_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("institutions.id"), index=True)
    creditor_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("creditors.id"), index=True)
    supplier_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("suppliers.id"))
    obligation_code: Mapped[str] = mapped_column(String(150), unique=True)
    obligation_type: Mapped[str] = mapped_column(String(40))
    description: Mapped[str] = mapped_column(Text)
    recognition_date: Mapped[date] = mapped_column(Date)
    due_date: Mapped[date | None] = mapped_column(Date, index=True)
    original_amount: Mapped[Decimal] = mapped_column(Money)
    outstanding_amount: Mapped[Decimal] = mapped_column(Money)
    paid_amount: Mapped[Decimal] = mapped_column(Money)
    currency: Mapped[str] = mapped_column(String(3))
    related_contract_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("procurement_contracts.id")
    )
    related_budget_execution_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("budget_execution_records.id")
    )
    status: Mapped[str] = mapped_column(String(30), index=True)
    legal_basis_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("legal_bases.id"))


class FinancialTransfer(Traceable, Audited, Base):
    __tablename__ = "financial_transfers"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    origin_institution_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("institutions.id"), index=True
    )
    destination_institution_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("institutions.id"), index=True
    )
    budget_cycle_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("budget_cycles.id"))
    transfer_code: Mapped[str] = mapped_column(String(150), unique=True)
    transfer_type: Mapped[str] = mapped_column(String(40), index=True)
    approval_date: Mapped[date] = mapped_column(Date)
    payment_date: Mapped[date | None] = mapped_column(Date, index=True)
    approved_amount: Mapped[Decimal] = mapped_column(Money)
    paid_amount: Mapped[Decimal] = mapped_column(Money)
    currency: Mapped[str] = mapped_column(String(3))
    purpose: Mapped[str] = mapped_column(Text)
    recurring: Mapped[bool] = mapped_column(Boolean)
    fiscal_year: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(30), index=True)
    legal_basis_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("legal_bases.id"))
    exception_documented: Mapped[bool] = mapped_column(Boolean, default=False)


class PublicSubsidy(Traceable, Audited, Base):
    __tablename__ = "public_subsidies"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    granting_institution_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("institutions.id"), index=True
    )
    beneficiary_institution_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("institutions.id")
    )
    beneficiary_supplier_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("suppliers.id"))
    program_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("budget_programs.id"))
    subsidy_code: Mapped[str] = mapped_column(String(150), unique=True)
    subsidy_type: Mapped[str] = mapped_column(String(40))
    period_start: Mapped[date] = mapped_column(Date)
    period_end: Mapped[date] = mapped_column(Date)
    approved_amount: Mapped[Decimal] = mapped_column(Money)
    paid_amount: Mapped[Decimal] = mapped_column(Money)
    currency: Mapped[str] = mapped_column(String(3))
    purpose: Mapped[str] = mapped_column(Text)
    eligibility_basis: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30))
    legal_basis_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("legal_bases.id"))


class MultiYearCommitment(Traceable, Audited, Base):
    __tablename__ = "multi_year_commitments"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    institution_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("institutions.id"), index=True)
    commitment_code: Mapped[str] = mapped_column(String(150), unique=True)
    related_contract_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("procurement_contracts.id")
    )
    related_project_id: Mapped[uuid.UUID | None]
    start_year: Mapped[int] = mapped_column(Integer)
    end_year: Mapped[int] = mapped_column(Integer)
    total_committed_amount: Mapped[Decimal] = mapped_column(Money)
    currency: Mapped[str] = mapped_column(String(3))
    annual_breakdown: Mapped[dict[str, object]] = mapped_column(Json)
    status: Mapped[str] = mapped_column(String(30))
    legal_basis_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("legal_bases.id"))


class DebtRestructuringEvent(Traceable, Base):
    __tablename__ = "debt_restructuring_events"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    original_instrument_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("debt_instruments.id"), index=True
    )
    replacement_instrument_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("debt_instruments.id")
    )
    event_type: Mapped[str] = mapped_column(String(30))
    effective_date: Mapped[date] = mapped_column(Date)
    principal_before: Mapped[Decimal] = mapped_column(Money)
    principal_after: Mapped[Decimal] = mapped_column(Money)
    maturity_before: Mapped[date | None] = mapped_column(Date)
    maturity_after: Mapped[date | None] = mapped_column(Date)
    interest_rate_before: Mapped[Decimal | None] = mapped_column(Rate)
    interest_rate_after: Mapped[Decimal | None] = mapped_column(Rate)
    description: Mapped[str] = mapped_column(Text)
    legal_basis_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("legal_bases.id"))
    status: Mapped[str] = mapped_column(String(30))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DebtVersion(Traceable, Base):
    __tablename__ = "debt_versions"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    entity_type: Mapped[str] = mapped_column(String(50), index=True)
    previous_entity_id: Mapped[uuid.UUID | None]
    new_entity_id: Mapped[uuid.UUID]
    reason: Mapped[str] = mapped_column(Text)
    effective_date: Mapped[date] = mapped_column(Date)
    actor: Mapped[str] = mapped_column(String(200))
    checksum: Mapped[str] = mapped_column(String(64), index=True)
    aggregate_differences: Mapped[dict[str, object]] = mapped_column(Json, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class FiscalRiskFinding(Base):
    __tablename__ = "fiscal_risk_findings"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    finding_type: Mapped[str] = mapped_column(String(50), index=True)
    severity: Mapped[str] = mapped_column(String(30), index=True)
    institution_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("institutions.id"), index=True)
    debt_instrument_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("debt_instruments.id"))
    guarantee_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("public_guarantees.id"))
    obligation_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("public_obligations.id"))
    transfer_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("financial_transfers.id"))
    observed_value: Mapped[dict[str, object]] = mapped_column(Json)
    expected_or_previous_value: Mapped[dict[str, object] | None] = mapped_column(Json)
    explanation: Mapped[str] = mapped_column(Text)
    evidence_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("evidence.id"))
    status: Mapped[str] = mapped_column(String(30), default="open")
    reviewer_notes: Mapped[str | None] = mapped_column(Text)
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", Json, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
