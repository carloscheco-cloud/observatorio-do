import uuid
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.db.base import Base

Json = JSON().with_variant(JSONB(), "postgresql")


class ProcurementType(StrEnum):
    GOODS = "goods"
    SERVICES = "services"
    WORKS = "works"
    CONSULTING = "consulting"
    CONCESSIONS = "concessions"
    LEASING = "leasing"
    MIXED = "mixed"
    OTHER = "other"


class ProcedureType(StrEnum):
    PUBLIC_TENDER = "public_tender"
    RESTRICTED_TENDER = "restricted_tender"
    PRICE_COMPARISON = "price_comparison"
    MINOR_PURCHASE = "minor_purchase"
    BELOW_THRESHOLD_PURCHASE = "below_threshold_purchase"
    DIRECT_CONTRACTING = "direct_contracting"
    EMERGENCY = "emergency"
    EXCEPTION = "exception"
    REVERSE_AUCTION = "reverse_auction"
    FRAMEWORK_AGREEMENT = "framework_agreement"
    LOTTERY = "lottery"
    OTHER = "other"


class ProcessStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    RECEIVING_OFFERS = "receiving_offers"
    EVALUATION = "evaluation"
    AWARDED = "awarded"
    PARTIALLY_AWARDED = "partially_awarded"
    CANCELLED = "cancelled"
    DESERTED = "deserted"
    SUSPENDED = "suspended"
    CLOSED = "closed"
    REPLACED = "replaced"
    UNDER_REVIEW = "under_review"


class Traceable:
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sources.id"))
    evidence_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("evidence.id"))
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", Json, default=dict)


class Audited:
    actor_type: Mapped[str] = mapped_column(String(30), default="human")
    validation_status: Mapped[str] = mapped_column(String(30), default="confirmed")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ProcurementProcess(Traceable, Audited, Base):
    __tablename__ = "procurement_processes"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    institution_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("institutions.id"))
    organizational_unit_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("organizational_units.id")
    )
    procurement_unit_name: Mapped[str | None] = mapped_column(String(300))
    process_code: Mapped[str] = mapped_column(String(150))
    external_reference: Mapped[str | None] = mapped_column(String(300))
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text)
    procurement_type: Mapped[ProcurementType] = mapped_column(Enum(ProcurementType))
    procedure_type: Mapped[ProcedureType] = mapped_column(Enum(ProcedureType))
    process_status: Mapped[ProcessStatus] = mapped_column(Enum(ProcessStatus))
    publication_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    submission_deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    opening_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    award_date: Mapped[date | None] = mapped_column(Date)
    estimated_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    currency: Mapped[str] = mapped_column(String(3))
    fiscal_year: Mapped[int] = mapped_column(Integer)
    territory_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("territories.id"))
    budget_cycle_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("budget_cycles.id"))
    budget_appropriation_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("budget_appropriations.id")
    )
    legal_basis_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("legal_bases.id"))
    raw_payload: Mapped[dict[str, object]] = mapped_column(Json, default=dict)
    row_location: Mapped[str | None] = mapped_column(String(300))
    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    version: Mapped[int] = mapped_column(Integer, default=1)
    checksum: Mapped[str | None] = mapped_column(String(64))


class ProcurementLot(Traceable, Base):
    __tablename__ = "procurement_lots"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    procurement_process_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("procurement_processes.id")
    )
    lot_number: Mapped[str] = mapped_column(String(50))
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str] = mapped_column(Text)
    estimated_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    awarded_amount: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    currency: Mapped[str] = mapped_column(String(3))
    status: Mapped[str] = mapped_column(String(30))
    multiple_awards: Mapped[bool] = mapped_column(Boolean, default=False)


class ProcurementItem(Traceable, Base):
    __tablename__ = "procurement_items"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    procurement_process_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("procurement_processes.id")
    )
    lot_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("procurement_lots.id"))
    item_code: Mapped[str | None] = mapped_column(String(100))
    classification_code: Mapped[str | None] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)
    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 4))
    unit_of_measure: Mapped[str] = mapped_column(String(50))
    estimated_unit_price: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    awarded_unit_price: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    estimated_total: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    awarded_total: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    currency: Mapped[str] = mapped_column(String(3))


class ProcurementBid(Traceable, Audited, Base):
    __tablename__ = "procurement_bids"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    procurement_process_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("procurement_processes.id")
    )
    lot_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("procurement_lots.id"))
    supplier_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("suppliers.id"))
    submission_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    offered_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    currency: Mapped[str] = mapped_column(String(3))
    bid_status: Mapped[str] = mapped_column(String(30))
    technical_score: Mapped[Decimal | None] = mapped_column(Numeric(7, 2))
    financial_score: Mapped[Decimal | None] = mapped_column(Numeric(7, 2))
    total_score: Mapped[Decimal | None] = mapped_column(Numeric(7, 2))
    is_compliant: Mapped[bool | None] = mapped_column(Boolean)
    rejection_reason: Mapped[str | None] = mapped_column(Text)


class ProcurementEvaluation(Traceable, Base):
    __tablename__ = "procurement_evaluations"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    procurement_process_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("procurement_processes.id")
    )
    bid_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("procurement_bids.id"))
    supplier_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("suppliers.id"))
    evaluation_type: Mapped[str] = mapped_column(String(30))
    criterion: Mapped[str] = mapped_column(Text)
    score: Mapped[Decimal | None] = mapped_column(Numeric(7, 2))
    maximum_score: Mapped[Decimal | None] = mapped_column(Numeric(7, 2))
    result: Mapped[str] = mapped_column(String(100))
    evaluator_reference: Mapped[str | None] = mapped_column(String(300))
    evaluation_date: Mapped[date] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ProcurementAward(Traceable, Audited, Base):
    __tablename__ = "procurement_awards"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    procurement_process_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("procurement_processes.id")
    )
    lot_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("procurement_lots.id"))
    supplier_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("suppliers.id"))
    bid_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("procurement_bids.id"))
    award_reference: Mapped[str] = mapped_column(String(150))
    award_date: Mapped[date] = mapped_column(Date)
    awarded_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    currency: Mapped[str] = mapped_column(String(3))
    award_status: Mapped[str] = mapped_column(String(30))
    legal_basis_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("legal_bases.id"))


class ProcurementContract(Traceable, Audited, Base):
    __tablename__ = "procurement_contracts"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    procurement_process_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("procurement_processes.id")
    )
    award_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("procurement_awards.id"))
    institution_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("institutions.id"))
    supplier_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("suppliers.id"))
    contract_code: Mapped[str] = mapped_column(String(150))
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text)
    signature_date: Mapped[date] = mapped_column(Date)
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    original_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    current_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    paid_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    currency: Mapped[str] = mapped_column(String(3))
    contract_status: Mapped[str] = mapped_column(String(30))
    procurement_type: Mapped[ProcurementType] = mapped_column(Enum(ProcurementType))
    territory_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("territories.id"))
    organizational_unit_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("organizational_units.id")
    )
    budget_cycle_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("budget_cycles.id"))
    budget_appropriation_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("budget_appropriations.id")
    )
    legal_basis_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("legal_bases.id"))
    raw_payload: Mapped[dict[str, object]] = mapped_column(Json, default=dict)
    exception_documented: Mapped[bool] = mapped_column(Boolean, default=False)
    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    version: Mapped[int] = mapped_column(Integer, default=1)
    checksum: Mapped[str | None] = mapped_column(String(64))


class ContractAmendment(Traceable, Audited, Base):
    __tablename__ = "contract_amendments"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    contract_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("procurement_contracts.id"))
    amendment_number: Mapped[str] = mapped_column(String(50))
    amendment_type: Mapped[str] = mapped_column(String(30))
    effective_date: Mapped[date] = mapped_column(Date)
    previous_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    new_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    previous_end_date: Mapped[date | None] = mapped_column(Date)
    new_end_date: Mapped[date | None] = mapped_column(Date)
    description: Mapped[str] = mapped_column(Text)
    legal_basis_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("legal_bases.id"))
    status: Mapped[str] = mapped_column(String(30))


class PurchaseOrder(Traceable, Base):
    __tablename__ = "purchase_orders"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    contract_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("procurement_contracts.id"))
    order_code: Mapped[str] = mapped_column(String(150))
    issue_date: Mapped[date] = mapped_column(Date)
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    currency: Mapped[str] = mapped_column(String(3))
    status: Mapped[str] = mapped_column(String(30))


class ContractDelivery(Traceable, Base):
    __tablename__ = "contract_deliveries"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    contract_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("procurement_contracts.id"))
    purchase_order_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("purchase_orders.id"))
    delivery_date: Mapped[date] = mapped_column(Date)
    acceptance_date: Mapped[date | None] = mapped_column(Date)
    delivered_amount: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    accepted_amount: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    status: Mapped[str] = mapped_column(String(30))
    description: Mapped[str] = mapped_column(Text)


class ContractPayment(Traceable, Base):
    __tablename__ = "contract_payments"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    contract_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("procurement_contracts.id"))
    institution_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("institutions.id"))
    supplier_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("suppliers.id"))
    payment_reference: Mapped[str] = mapped_column(String(150))
    payment_date: Mapped[date] = mapped_column(Date)
    gross_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    deductions: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    net_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    currency: Mapped[str] = mapped_column(String(3))
    budget_execution_record_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("budget_execution_records.id")
    )
    status: Mapped[str] = mapped_column(String(30))
    exception_documented: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ContractGuarantee(Traceable, Base):
    __tablename__ = "contract_guarantees"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    procurement_process_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("procurement_processes.id")
    )
    contract_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("procurement_contracts.id"))
    supplier_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("suppliers.id"))
    guarantee_type: Mapped[str] = mapped_column(String(30))
    issuer_name: Mapped[str] = mapped_column(String(300))
    reference_hash: Mapped[str | None] = mapped_column(String(64))
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    currency: Mapped[str] = mapped_column(String(3))
    issue_date: Mapped[date] = mapped_column(Date)
    expiration_date: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(30))


class ProcurementChallenge(Traceable, Audited, Base):
    __tablename__ = "procurement_challenges"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    procurement_process_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("procurement_processes.id")
    )
    supplier_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("suppliers.id"))
    challenge_type: Mapped[str] = mapped_column(String(50))
    filing_date: Mapped[date] = mapped_column(Date)
    decision_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(30))
    summary: Mapped[str] = mapped_column(Text)
    decision_summary: Mapped[str | None] = mapped_column(Text)
    legal_basis_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("legal_bases.id"))


class ProcurementVersion(Traceable, Base):
    __tablename__ = "procurement_versions"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    entity_type: Mapped[str] = mapped_column(String(50))
    previous_entity_id: Mapped[uuid.UUID | None]
    new_entity_id: Mapped[uuid.UUID]
    change_type: Mapped[str] = mapped_column(String(30))
    reason: Mapped[str] = mapped_column(Text)
    effective_date: Mapped[date] = mapped_column(Date)
    actor: Mapped[str] = mapped_column(String(200))
    checksum: Mapped[str] = mapped_column(String(64))
    aggregate_differences: Mapped[dict[str, object]] = mapped_column(Json, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ProcurementFinding(Base):
    __tablename__ = "procurement_findings"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    finding_type: Mapped[str] = mapped_column(String(50))
    severity: Mapped[str] = mapped_column(String(30))
    institution_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("institutions.id"))
    procurement_process_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("procurement_processes.id")
    )
    contract_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("procurement_contracts.id"))
    supplier_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("suppliers.id"))
    observed_value: Mapped[dict[str, object]] = mapped_column(Json, default=dict)
    expected_or_previous_value: Mapped[dict[str, object] | None] = mapped_column(Json)
    explanation: Mapped[str] = mapped_column(Text)
    evidence_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("evidence.id"))
    status: Mapped[str] = mapped_column(String(30), default="open")
    reviewer_notes: Mapped[str | None] = mapped_column(Text)
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", Json, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
