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
Measure = Numeric(20, 6)
Percent = Numeric(7, 4)


class Traceable:
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sources.id"))
    evidence_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("evidence.id"))
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", Json, default=dict)


class Audited:
    actor_type: Mapped[str] = mapped_column(String(30), default="human")
    validation_status: Mapped[str] = mapped_column(String(30), default="confirmed")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AssetLocation(Traceable, Audited, Base):
    __tablename__ = "asset_locations"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    institution_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("institutions.id"), index=True)
    territory_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("territories.id"), index=True)
    organizational_unit_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("organizational_units.id")
    )
    location_type: Mapped[str] = mapped_column(String(40))
    official_name: Mapped[str] = mapped_column(String(300))
    address_public: Mapped[str | None] = mapped_column(Text)
    geographic_reference: Mapped[str | None] = mapped_column(String(300))
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7))
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7))
    parent_location_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("asset_locations.id"))
    status: Mapped[str] = mapped_column(String(30), index=True)
    is_restricted: Mapped[bool] = mapped_column(Boolean, default=False)


class PublicAsset(Traceable, Audited, Base):
    __tablename__ = "public_assets"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    owner_institution_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("institutions.id"), index=True
    )
    managing_institution_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("institutions.id"), index=True
    )
    organizational_unit_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("organizational_units.id"), index=True
    )
    asset_category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("asset_categories.id"), index=True
    )
    asset_code: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    external_reference: Mapped[str | None] = mapped_column(String(300))
    official_name: Mapped[str] = mapped_column(String(500))
    normalized_name: Mapped[str] = mapped_column(String(500), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    acquisition_method: Mapped[str] = mapped_column(String(40), index=True)
    acquisition_date: Mapped[date | None] = mapped_column(Date, index=True)
    commissioning_date: Mapped[date | None] = mapped_column(Date)
    original_cost: Mapped[Decimal | None] = mapped_column(Money)
    current_book_value: Mapped[Decimal | None] = mapped_column(Money)
    estimated_market_value: Mapped[Decimal | None] = mapped_column(Money)
    currency: Mapped[str] = mapped_column(String(3), default="DOP")
    quantity: Mapped[Decimal] = mapped_column(Measure, default=Decimal("1"))
    unit_of_measure: Mapped[str] = mapped_column(String(30), default="unit")
    status: Mapped[str] = mapped_column(String(30), index=True)
    condition_status: Mapped[str] = mapped_column(String(30), index=True)
    ownership_status: Mapped[str] = mapped_column(String(30))
    territory_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("territories.id"), index=True)
    location_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("asset_locations.id"), index=True
    )
    custodian_person_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("persons.id"), index=True
    )
    custodian_position_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("positions.id"))
    useful_life_years: Mapped[int | None] = mapped_column(Integer)
    residual_value: Mapped[Decimal | None] = mapped_column(Money)
    depreciation_method: Mapped[str | None] = mapped_column(String(40))
    legal_basis_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("legal_bases.id"))
    raw_payload: Mapped[dict[str, object]] = mapped_column(Json, default=dict)
    row_location: Mapped[str | None] = mapped_column(String(300))
    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    version: Mapped[int] = mapped_column(Integer, default=1)
    checksum: Mapped[str | None] = mapped_column(String(64), index=True)


class RealEstateAsset(Base):
    __tablename__ = "real_estate_assets"
    asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("public_assets.id"), primary_key=True)
    property_type: Mapped[str] = mapped_column(String(40))
    land_area: Mapped[Decimal | None] = mapped_column(Measure)
    built_area: Mapped[Decimal | None] = mapped_column(Measure)
    unit_of_area: Mapped[str] = mapped_column(String(20), default="m2")
    registry_reference_hash: Mapped[str | None] = mapped_column(String(64))
    cadastral_reference_hash: Mapped[str | None] = mapped_column(String(64))
    title_status: Mapped[str] = mapped_column(String(30))
    occupancy_status: Mapped[str] = mapped_column(String(30))
    zoning: Mapped[str | None] = mapped_column(String(100))
    construction_year: Mapped[int | None] = mapped_column(Integer)
    number_of_buildings: Mapped[int | None] = mapped_column(Integer)
    number_of_floors: Mapped[int | None] = mapped_column(Integer)
    appraised_value: Mapped[Decimal | None] = mapped_column(Money)
    appraisal_date: Mapped[date | None] = mapped_column(Date)
    encumbrance_status: Mapped[str] = mapped_column(String(30))
    parent_land_asset_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("public_assets.id"))
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", Json, default=dict)


class VehicleAsset(Base):
    __tablename__ = "vehicle_assets"
    asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("public_assets.id"), primary_key=True)
    vehicle_type: Mapped[str] = mapped_column(String(40))
    make: Mapped[str | None] = mapped_column(String(100))
    model: Mapped[str | None] = mapped_column(String(100))
    year: Mapped[int | None] = mapped_column(Integer)
    fuel_type: Mapped[str | None] = mapped_column(String(30))
    color: Mapped[str | None] = mapped_column(String(50))
    plate_reference_masked: Mapped[str | None] = mapped_column(String(30))
    vin_hash: Mapped[str | None] = mapped_column(String(64), index=True)
    engine_reference_hash: Mapped[str | None] = mapped_column(String(64))
    mileage: Mapped[Decimal | None] = mapped_column(Measure)
    mileage_date: Mapped[date | None] = mapped_column(Date)
    operational_status: Mapped[str] = mapped_column(String(30))
    assigned_unit_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("organizational_units.id")
    )
    assigned_person_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("persons.id"))
    insurance_status: Mapped[str] = mapped_column(String(30))
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", Json, default=dict)


class EquipmentAsset(Base):
    __tablename__ = "equipment_assets"
    asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("public_assets.id"), primary_key=True)
    equipment_type: Mapped[str] = mapped_column(String(50))
    manufacturer: Mapped[str | None] = mapped_column(String(150))
    model: Mapped[str | None] = mapped_column(String(150))
    serial_reference_hash: Mapped[str | None] = mapped_column(String(64), index=True)
    technical_specifications: Mapped[dict[str, object]] = mapped_column(Json, default=dict)
    warranty_start: Mapped[date | None] = mapped_column(Date)
    warranty_end: Mapped[date | None] = mapped_column(Date)
    support_end: Mapped[date | None] = mapped_column(Date)
    software_license_reference_hash: Mapped[str | None] = mapped_column(String(64))
    assigned_unit_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("organizational_units.id")
    )
    assigned_person_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("persons.id"))
    operational_status: Mapped[str] = mapped_column(String(30))
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", Json, default=dict)


class InfrastructureAsset(Base):
    __tablename__ = "infrastructure_assets"
    asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("public_assets.id"), primary_key=True)
    infrastructure_type: Mapped[str] = mapped_column(String(50))
    project_id: Mapped[uuid.UUID | None]
    contract_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("procurement_contracts.id"))
    budget_cycle_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("budget_cycles.id"))
    construction_start_date: Mapped[date | None] = mapped_column(Date)
    completion_date: Mapped[date | None] = mapped_column(Date)
    operational_start_date: Mapped[date | None] = mapped_column(Date)
    physical_progress_percentage: Mapped[Decimal | None] = mapped_column(Percent)
    financial_progress_percentage: Mapped[Decimal | None] = mapped_column(Percent)
    contractor_supplier_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("suppliers.id"))
    supervising_institution_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("institutions.id")
    )
    capacity_description: Mapped[str | None] = mapped_column(Text)
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", Json, default=dict)


class IntangibleAsset(Base):
    __tablename__ = "intangible_assets"
    asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("public_assets.id"), primary_key=True)
    intangible_type: Mapped[str] = mapped_column(String(40))
    license_type: Mapped[str | None] = mapped_column(String(40))
    vendor_supplier_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("suppliers.id"))
    start_date: Mapped[date | None] = mapped_column(Date)
    expiration_date: Mapped[date | None] = mapped_column(Date)
    renewal_date: Mapped[date | None] = mapped_column(Date)
    number_of_users: Mapped[int | None] = mapped_column(Integer)
    annual_cost: Mapped[Decimal | None] = mapped_column(Money)
    ownership_or_license_status: Mapped[str] = mapped_column(String(40))
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", Json, default=dict)


class AssetAssignment(Traceable, Audited, Base):
    __tablename__ = "asset_assignments"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("public_assets.id"), index=True)
    institution_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("institutions.id"), index=True)
    organizational_unit_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("organizational_units.id")
    )
    person_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("persons.id"))
    position_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("positions.id"))
    assignment_type: Mapped[str] = mapped_column(String(40))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(30), index=True)
    responsibility_description: Mapped[str | None] = mapped_column(Text)


class AssetTransfer(Traceable, Audited, Base):
    __tablename__ = "asset_transfers"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("public_assets.id"), index=True)
    origin_institution_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("institutions.id"))
    destination_institution_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("institutions.id"))
    origin_unit_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("organizational_units.id"))
    destination_unit_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("organizational_units.id")
    )
    transfer_type: Mapped[str] = mapped_column(String(40))
    approval_date: Mapped[date] = mapped_column(Date)
    effective_date: Mapped[date] = mapped_column(Date)
    previous_book_value: Mapped[Decimal | None] = mapped_column(Money)
    transferred_value: Mapped[Decimal | None] = mapped_column(Money)
    currency: Mapped[str] = mapped_column(String(3))
    legal_basis_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("legal_bases.id"))
    status: Mapped[str] = mapped_column(String(30))
    description: Mapped[str] = mapped_column(Text)


class AssetEvent(Traceable, Base):
    __tablename__ = "asset_events"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("public_assets.id"), index=True)
    institution_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("institutions.id"))
    event_type: Mapped[str] = mapped_column(String(40), index=True)
    event_date: Mapped[date] = mapped_column(Date, index=True)
    previous_status: Mapped[str | None] = mapped_column(String(30))
    new_status: Mapped[str | None] = mapped_column(String(30))
    previous_location_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("asset_locations.id"))
    new_location_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("asset_locations.id"))
    amount: Mapped[Decimal | None] = mapped_column(Money)
    currency: Mapped[str | None] = mapped_column(String(3))
    description: Mapped[str] = mapped_column(Text)
    legal_basis_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("legal_bases.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AssetMaintenanceRecord(Traceable, Audited, Base):
    __tablename__ = "asset_maintenance_records"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("public_assets.id"), index=True)
    institution_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("institutions.id"))
    maintenance_type: Mapped[str] = mapped_column(String(40))
    scheduled_date: Mapped[date | None] = mapped_column(Date)
    performed_date: Mapped[date | None] = mapped_column(Date)
    provider_supplier_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("suppliers.id"))
    contract_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("procurement_contracts.id"))
    description: Mapped[str] = mapped_column(Text)
    cost: Mapped[Decimal] = mapped_column(Money)
    currency: Mapped[str] = mapped_column(String(3))
    odometer_or_usage: Mapped[Decimal | None] = mapped_column(Measure)
    status: Mapped[str] = mapped_column(String(30), index=True)


class AssetValuation(Traceable, Base):
    __tablename__ = "asset_valuations"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("public_assets.id"), index=True)
    valuation_date: Mapped[date] = mapped_column(Date, index=True)
    valuation_type: Mapped[str] = mapped_column(String(40))
    gross_value: Mapped[Decimal] = mapped_column(Money)
    accumulated_depreciation: Mapped[Decimal] = mapped_column(Money)
    impairment_amount: Mapped[Decimal] = mapped_column(Money)
    net_book_value: Mapped[Decimal] = mapped_column(Money)
    market_value: Mapped[Decimal | None] = mapped_column(Money)
    residual_value: Mapped[Decimal | None] = mapped_column(Money)
    currency: Mapped[str] = mapped_column(String(3))
    valuation_method: Mapped[str] = mapped_column(String(50))
    appraiser_reference: Mapped[str | None] = mapped_column(String(200))
    version: Mapped[int] = mapped_column(Integer, default=1)
    checksum: Mapped[str | None] = mapped_column(String(64), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AssetInsurancePolicy(Traceable, Audited, Base):
    __tablename__ = "asset_insurance_policies"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("public_assets.id"), index=True)
    insurer_supplier_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("suppliers.id"))
    policy_reference_hash: Mapped[str | None] = mapped_column(String(64))
    coverage_type: Mapped[str] = mapped_column(String(50))
    coverage_start: Mapped[date] = mapped_column(Date)
    coverage_end: Mapped[date] = mapped_column(Date)
    insured_value: Mapped[Decimal] = mapped_column(Money)
    premium_amount: Mapped[Decimal] = mapped_column(Money)
    currency: Mapped[str] = mapped_column(String(3))
    status: Mapped[str] = mapped_column(String(30))


class AssetEncumbrance(Traceable, Audited, Base):
    __tablename__ = "asset_encumbrances"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("public_assets.id"), index=True)
    encumbrance_type: Mapped[str] = mapped_column(String(40))
    creditor_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("creditors.id"))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    amount: Mapped[Decimal | None] = mapped_column(Money)
    currency: Mapped[str | None] = mapped_column(String(3))
    status: Mapped[str] = mapped_column(String(30))
    legal_basis_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("legal_bases.id"))
    description: Mapped[str] = mapped_column(Text)


class PhysicalInventory(Traceable, Audited, Base):
    __tablename__ = "physical_inventories"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    institution_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("institutions.id"), index=True)
    organizational_unit_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("organizational_units.id")
    )
    location_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("asset_locations.id"))
    inventory_code: Mapped[str] = mapped_column(String(150), unique=True)
    inventory_date: Mapped[date] = mapped_column(Date, index=True)
    scope: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30))
    expected_asset_count: Mapped[int] = mapped_column(Integer)
    observed_asset_count: Mapped[int] = mapped_column(Integer)
    matched_count: Mapped[int] = mapped_column(Integer)
    missing_count: Mapped[int] = mapped_column(Integer)
    surplus_count: Mapped[int] = mapped_column(Integer)


class PhysicalInventoryItem(Base):
    __tablename__ = "physical_inventory_items"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    physical_inventory_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("physical_inventories.id"), index=True
    )
    asset_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("public_assets.id"))
    observed_reference: Mapped[str] = mapped_column(String(200))
    observed_name: Mapped[str] = mapped_column(String(500))
    observed_condition: Mapped[str] = mapped_column(String(30))
    observed_location_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("asset_locations.id"))
    match_status: Mapped[str] = mapped_column(String(40))
    discrepancy_type: Mapped[str | None] = mapped_column(String(40))
    notes: Mapped[str | None] = mapped_column(Text)
    evidence_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("evidence.id"))
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", Json, default=dict)


class AssetDisposal(Traceable, Audited, Base):
    __tablename__ = "asset_disposals"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("public_assets.id"), index=True)
    institution_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("institutions.id"))
    disposal_type: Mapped[str] = mapped_column(String(40))
    approval_date: Mapped[date] = mapped_column(Date)
    effective_date: Mapped[date] = mapped_column(Date)
    book_value: Mapped[Decimal] = mapped_column(Money)
    disposal_value: Mapped[Decimal | None] = mapped_column(Money)
    currency: Mapped[str] = mapped_column(String(3))
    buyer_supplier_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("suppliers.id"))
    destination_institution_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("institutions.id")
    )
    reason: Mapped[str] = mapped_column(Text)
    legal_basis_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("legal_bases.id"))
    status: Mapped[str] = mapped_column(String(30))


class AssetVersion(Traceable, Base):
    __tablename__ = "asset_versions"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    entity_type: Mapped[str] = mapped_column(String(50), index=True)
    previous_entity_id: Mapped[uuid.UUID | None]
    new_entity_id: Mapped[uuid.UUID]
    change_type: Mapped[str] = mapped_column(String(40))
    reason: Mapped[str] = mapped_column(Text)
    effective_date: Mapped[date] = mapped_column(Date)
    actor: Mapped[str] = mapped_column(String(200))
    checksum: Mapped[str] = mapped_column(String(64), index=True)
    aggregate_differences: Mapped[dict[str, object]] = mapped_column(Json, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AssetFinding(Base):
    __tablename__ = "asset_findings"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    finding_type: Mapped[str] = mapped_column(String(60), index=True)
    severity: Mapped[str] = mapped_column(String(30), index=True)
    institution_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("institutions.id"), index=True)
    asset_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("public_assets.id"))
    inventory_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("physical_inventories.id"))
    maintenance_record_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("asset_maintenance_records.id")
    )
    observed_value: Mapped[dict[str, object]] = mapped_column(Json)
    expected_or_previous_value: Mapped[dict[str, object] | None] = mapped_column(Json)
    explanation: Mapped[str] = mapped_column(Text)
    evidence_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("evidence.id"))
    status: Mapped[str] = mapped_column(String(30), default="open")
    reviewer_notes: Mapped[str | None] = mapped_column(Text)
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", Json, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
