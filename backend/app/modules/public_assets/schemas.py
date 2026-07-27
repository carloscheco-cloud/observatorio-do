import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TraceCreate(BaseModel):
    source_id: uuid.UUID
    evidence_id: uuid.UUID
    metadata_: dict[str, object] = Field(default_factory=dict, alias="metadata")


class AssetCreate(TraceCreate):
    owner_institution_id: uuid.UUID
    managing_institution_id: uuid.UUID | None = None
    organizational_unit_id: uuid.UUID | None = None
    asset_category_id: uuid.UUID
    asset_code: str = Field(min_length=1, max_length=150)
    external_reference: str | None = None
    official_name: str = Field(min_length=1)
    normalized_name: str = Field(min_length=1)
    description: str | None = None
    acquisition_method: str
    acquisition_date: date | None = None
    commissioning_date: date | None = None
    original_cost: Decimal | None = Field(None, ge=0)
    current_book_value: Decimal | None = Field(None, ge=0)
    estimated_market_value: Decimal | None = Field(None, ge=0)
    currency: str = Field("DOP", pattern=r"^[A-Z]{3}$")
    quantity: Decimal = Field(Decimal("1"), ge=0)
    unit_of_measure: str = "unit"
    status: str = "draft"
    condition_status: str = "unknown"
    ownership_status: str = "owned"
    territory_id: uuid.UUID | None = None
    location_id: uuid.UUID | None = None
    custodian_person_id: uuid.UUID | None = None
    custodian_position_id: uuid.UUID | None = None
    useful_life_years: int | None = Field(None, ge=0)
    residual_value: Decimal | None = Field(None, ge=0)
    depreciation_method: str | None = None
    legal_basis_id: uuid.UUID | None = None
    raw_payload: dict[str, object] = Field(default_factory=dict, exclude=True)
    row_location: str | None = None
    version: int = Field(1, ge=1)
    checksum: str | None = Field(None, pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def dates(self) -> "AssetCreate":
        if (
            self.commissioning_date
            and self.acquisition_date
            and self.commissioning_date < self.acquisition_date
        ):
            raise ValueError("commissioning_date cannot precede acquisition_date")
        return self


class AssetRead(AssetCreate):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class LocationCreate(TraceCreate):
    institution_id: uuid.UUID
    territory_id: uuid.UUID | None = None
    organizational_unit_id: uuid.UUID | None = None
    location_type: str
    official_name: str
    address_public: str | None = None
    geographic_reference: str | None = None
    latitude: Decimal | None = Field(None, ge=-90, le=90)
    longitude: Decimal | None = Field(None, ge=-180, le=180)
    parent_location_id: uuid.UUID | None = None
    status: str = "active"
    is_restricted: bool = False


class AssignmentCreate(TraceCreate):
    asset_id: uuid.UUID
    institution_id: uuid.UUID
    organizational_unit_id: uuid.UUID | None = None
    person_id: uuid.UUID | None = None
    position_id: uuid.UUID | None = None
    assignment_type: str
    start_date: date
    end_date: date | None = None
    status: str = "active"
    responsibility_description: str | None = None

    @model_validator(mode="after")
    def dates(self) -> "AssignmentCreate":
        if self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date cannot precede start_date")
        return self


class TransferCreate(TraceCreate):
    asset_id: uuid.UUID
    origin_institution_id: uuid.UUID
    destination_institution_id: uuid.UUID
    origin_unit_id: uuid.UUID | None = None
    destination_unit_id: uuid.UUID | None = None
    transfer_type: str
    approval_date: date
    effective_date: date
    previous_book_value: Decimal | None = Field(None, ge=0)
    transferred_value: Decimal | None = Field(None, ge=0)
    currency: str = Field("DOP", pattern=r"^[A-Z]{3}$")
    legal_basis_id: uuid.UUID
    status: str = "draft"
    description: str

    @model_validator(mode="after")
    def coherent(self) -> "TransferCreate":
        if (
            self.origin_institution_id == self.destination_institution_id
            and self.transfer_type != "reassignment"
        ):
            raise ValueError("origin and destination must differ")
        if self.effective_date < self.approval_date:
            raise ValueError("effective_date cannot precede approval_date")
        return self


class MaintenanceCreate(TraceCreate):
    asset_id: uuid.UUID
    institution_id: uuid.UUID
    maintenance_type: str
    scheduled_date: date | None = None
    performed_date: date | None = None
    provider_supplier_id: uuid.UUID | None = None
    contract_id: uuid.UUID | None = None
    description: str
    cost: Decimal = Field(ge=0)
    currency: str = Field("DOP", pattern=r"^[A-Z]{3}$")
    odometer_or_usage: Decimal | None = Field(None, ge=0)
    status: str


class ValuationCreate(TraceCreate):
    asset_id: uuid.UUID
    valuation_date: date
    valuation_type: str
    gross_value: Decimal = Field(ge=0)
    accumulated_depreciation: Decimal = Field(ge=0)
    impairment_amount: Decimal = Field(ge=0)
    net_book_value: Decimal = Field(ge=0)
    market_value: Decimal | None = Field(None, ge=0)
    residual_value: Decimal | None = Field(None, ge=0)
    currency: str = Field("DOP", pattern=r"^[A-Z]{3}$")
    valuation_method: str
    appraiser_reference: str | None = None
    version: int = Field(1, ge=1)
    checksum: str | None = Field(None, pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def formula(self) -> "ValuationCreate":
        expected = self.gross_value - self.accumulated_depreciation - self.impairment_amount
        if self.net_book_value != expected:
            raise ValueError("net_book_value is inconsistent")
        return self


class InventoryCreate(TraceCreate):
    institution_id: uuid.UUID
    organizational_unit_id: uuid.UUID | None = None
    location_id: uuid.UUID | None = None
    inventory_code: str
    inventory_date: date
    scope: str
    status: str
    expected_asset_count: int = Field(ge=0)
    observed_asset_count: int = Field(ge=0)
    matched_count: int = Field(ge=0)
    missing_count: int = Field(ge=0)
    surplus_count: int = Field(ge=0)


class DisposalCreate(TraceCreate):
    asset_id: uuid.UUID
    institution_id: uuid.UUID
    disposal_type: str
    approval_date: date
    effective_date: date
    book_value: Decimal = Field(ge=0)
    disposal_value: Decimal | None = Field(None, ge=0)
    currency: str = Field("DOP", pattern=r"^[A-Z]{3}$")
    buyer_supplier_id: uuid.UUID | None = None
    destination_institution_id: uuid.UUID | None = None
    reason: str
    legal_basis_id: uuid.UUID
    status: str

    @model_validator(mode="after")
    def dates(self) -> "DisposalCreate":
        if self.effective_date < self.approval_date:
            raise ValueError("effective_date cannot precede approval_date")
        return self


class GenericRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: uuid.UUID


class FindingReview(BaseModel):
    status: str
    reviewer_notes: str | None = None


class AssetMetrics(BaseModel):
    asset_count: int
    original_value: Decimal
    book_value: Decimal
    estimated_value: Decimal
    maintenance_cost: Decimal
    without_custodian: int
    insured_count: int
