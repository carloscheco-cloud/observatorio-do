# ruff: noqa: E501
"""Block 9: public assets, patrimony, custody, maintenance and disposal.

Revision ID: 0009
Revises: 0008
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0009"
down_revision: str | None = "0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TABLES = (
    "asset_categories",
    "asset_locations",
    "public_assets",
    "real_estate_assets",
    "vehicle_assets",
    "equipment_assets",
    "infrastructure_assets",
    "intangible_assets",
    "asset_assignments",
    "asset_transfers",
    "asset_events",
    "asset_maintenance_records",
    "asset_valuations",
    "asset_insurance_policies",
    "asset_encumbrances",
    "physical_inventories",
    "physical_inventory_items",
    "asset_disposals",
    "asset_versions",
    "asset_findings",
)


def upgrade() -> None:
    from app.db.base import Base
    from app.modules import models  # noqa: F401

    bind = op.get_bind()
    for name in TABLES:
        Base.metadata.tables[name].create(bind=bind)

    constraints = {
        "asset_categories": [
            "CONSTRAINT ck_asset_category_dates CHECK (valid_to IS NULL OR valid_to >= valid_from)",
            "CONSTRAINT ck_asset_category_life CHECK (default_useful_life_years IS NULL OR default_useful_life_years >= 0)",
            "CONSTRAINT ck_asset_category_self CHECK (parent_id IS NULL OR parent_id <> id)",
        ],
        "asset_locations": [
            "CONSTRAINT ck_asset_location_self CHECK (parent_location_id IS NULL OR parent_location_id <> id)",
            "CONSTRAINT ck_asset_latitude CHECK (latitude IS NULL OR latitude BETWEEN -90 AND 90)",
            "CONSTRAINT ck_asset_longitude CHECK (longitude IS NULL OR longitude BETWEEN -180 AND 180)",
            "CONSTRAINT ck_restricted_address CHECK (NOT is_restricted OR address_public IS NULL)",
        ],
        "public_assets": [
            "CONSTRAINT ck_asset_values CHECK (quantity >= 0 AND coalesce(original_cost,0) >= 0 AND coalesce(current_book_value,0) >= 0 AND coalesce(estimated_market_value,0) >= 0 AND coalesce(residual_value,0) >= 0)",
            "CONSTRAINT ck_asset_dates CHECK (commissioning_date IS NULL OR acquisition_date IS NULL OR commissioning_date >= acquisition_date)",
            "CONSTRAINT ck_asset_currency CHECK (currency ~ '^[A-Z]{3}$')",
            "CONSTRAINT uq_asset_canonical UNIQUE (owner_institution_id, asset_code)",
        ],
        "real_estate_assets": [
            "CONSTRAINT ck_real_estate_values CHECK (coalesce(land_area,0) >= 0 AND coalesce(built_area,0) >= 0 AND coalesce(appraised_value,0) >= 0)",
            "CONSTRAINT ck_registry_hash CHECK (registry_reference_hash IS NULL OR registry_reference_hash ~ '^[0-9a-f]{64}$')",
            "CONSTRAINT ck_cadastral_hash CHECK (cadastral_reference_hash IS NULL OR cadastral_reference_hash ~ '^[0-9a-f]{64}$')",
        ],
        "vehicle_assets": [
            "CONSTRAINT ck_vehicle_mileage CHECK (mileage IS NULL OR mileage >= 0)",
            "CONSTRAINT ck_vehicle_vin_hash CHECK (vin_hash IS NULL OR vin_hash ~ '^[0-9a-f]{64}$')",
            "CONSTRAINT ck_vehicle_engine_hash CHECK (engine_reference_hash IS NULL OR engine_reference_hash ~ '^[0-9a-f]{64}$')",
        ],
        "equipment_assets": [
            "CONSTRAINT ck_equipment_warranty CHECK (warranty_end IS NULL OR warranty_start IS NULL OR warranty_end >= warranty_start)",
            "CONSTRAINT ck_equipment_serial_hash CHECK (serial_reference_hash IS NULL OR serial_reference_hash ~ '^[0-9a-f]{64}$')",
        ],
        "infrastructure_assets": [
            "CONSTRAINT ck_infrastructure_progress CHECK (coalesce(physical_progress_percentage,0) BETWEEN 0 AND 100 AND coalesce(financial_progress_percentage,0) BETWEEN 0 AND 100)",
            "CONSTRAINT ck_infrastructure_dates CHECK ((completion_date IS NULL OR construction_start_date IS NULL OR completion_date >= construction_start_date) AND (operational_start_date IS NULL OR completion_date IS NULL OR operational_start_date >= completion_date))",
        ],
        "intangible_assets": [
            "CONSTRAINT ck_intangible_dates CHECK (expiration_date IS NULL OR start_date IS NULL OR expiration_date >= start_date)",
            "CONSTRAINT ck_intangible_values CHECK (coalesce(number_of_users,0) >= 0 AND coalesce(annual_cost,0) >= 0)",
        ],
        "asset_assignments": [
            "CONSTRAINT ck_assignment_dates CHECK (end_date IS NULL OR end_date >= start_date)",
        ],
        "asset_transfers": [
            "CONSTRAINT ck_asset_transfer_entities CHECK (origin_institution_id <> destination_institution_id OR transfer_type = 'reassignment')",
            "CONSTRAINT ck_asset_transfer_dates CHECK (effective_date >= approval_date)",
            "CONSTRAINT ck_asset_transfer_values CHECK (coalesce(previous_book_value,0) >= 0 AND coalesce(transferred_value,0) >= 0)",
        ],
        "asset_events": ["CONSTRAINT ck_asset_event_amount CHECK (amount IS NULL OR amount >= 0)"],
        "asset_maintenance_records": [
            "CONSTRAINT ck_asset_maintenance_cost CHECK (cost >= 0 AND coalesce(odometer_or_usage,0) >= 0)",
        ],
        "asset_valuations": [
            "CONSTRAINT ck_asset_valuation_values CHECK (gross_value >= 0 AND accumulated_depreciation >= 0 AND impairment_amount >= 0 AND net_book_value >= 0 AND coalesce(market_value,0) >= 0 AND coalesce(residual_value,0) >= 0)",
            "CONSTRAINT ck_asset_valuation_formula CHECK (net_book_value = gross_value - accumulated_depreciation - impairment_amount)",
            "CONSTRAINT uq_asset_valuation_version UNIQUE (asset_id, valuation_date, valuation_type, version)",
        ],
        "asset_insurance_policies": [
            "CONSTRAINT ck_asset_insurance_dates CHECK (coverage_end >= coverage_start)",
            "CONSTRAINT ck_asset_insurance_values CHECK (insured_value >= 0 AND premium_amount >= 0)",
            "CONSTRAINT ck_policy_hash CHECK (policy_reference_hash IS NULL OR policy_reference_hash ~ '^[0-9a-f]{64}$')",
        ],
        "asset_encumbrances": [
            "CONSTRAINT ck_asset_encumbrance_dates CHECK (end_date IS NULL OR end_date >= start_date)",
            "CONSTRAINT ck_asset_encumbrance_amount CHECK (amount IS NULL OR amount >= 0)",
        ],
        "physical_inventories": [
            "CONSTRAINT ck_inventory_counts CHECK (expected_asset_count >= 0 AND observed_asset_count >= 0 AND matched_count >= 0 AND missing_count >= 0 AND surplus_count >= 0 AND matched_count + missing_count <= expected_asset_count AND matched_count + surplus_count <= observed_asset_count)",
        ],
        "asset_disposals": [
            "CONSTRAINT ck_asset_disposal_dates CHECK (effective_date >= approval_date)",
            "CONSTRAINT ck_asset_disposal_values CHECK (book_value >= 0 AND coalesce(disposal_value,0) >= 0)",
        ],
    }
    for table, clauses in constraints.items():
        for clause in clauses:
            op.execute(f"ALTER TABLE {table} ADD {clause}")

    op.execute("""
    CREATE FUNCTION public_asset_trace_guard() RETURNS trigger AS $$
    DECLARE evidence_source uuid;
    BEGIN
      IF current_setting('app.actor_type', true) = 'ai'
         OR (to_jsonb(NEW) ? 'actor_type' AND to_jsonb(NEW)->>'actor_type' = 'ai') THEN
        RAISE EXCEPTION 'AI actors cannot write canonical public asset data';
      END IF;
      IF NEW.source_id IS NULL OR NEW.evidence_id IS NULL THEN
        RAISE EXCEPTION 'Canonical public asset data requires source and evidence';
      END IF;
      SELECT source_id INTO evidence_source FROM evidence WHERE id = NEW.evidence_id;
      IF evidence_source IS DISTINCT FROM NEW.source_id THEN
        RAISE EXCEPTION 'Source must match evidence source';
      END IF;
      RETURN NEW;
    END; $$ LANGUAGE plpgsql;
    """)
    canonical = (
        "asset_categories",
        "asset_locations",
        "public_assets",
        "asset_assignments",
        "asset_transfers",
        "asset_maintenance_records",
        "asset_valuations",
        "asset_insurance_policies",
        "asset_encumbrances",
        "physical_inventories",
        "asset_disposals",
        "asset_versions",
    )
    for table in canonical:
        op.execute(
            f"CREATE TRIGGER trg_{table}_trace BEFORE INSERT OR UPDATE ON {table} "
            "FOR EACH ROW EXECUTE FUNCTION public_asset_trace_guard()"
        )

    op.execute("""
    CREATE FUNCTION asset_institution_guard() RETURNS trigger AS $$
    DECLARE unit_institution uuid; location_institution uuid; asset_owner uuid; asset_manager uuid;
            unit_ref uuid; location_ref uuid; institution_ref uuid; asset_ref uuid;
    BEGIN
      unit_ref := (to_jsonb(NEW)->>'organizational_unit_id')::uuid;
      location_ref := (to_jsonb(NEW)->>'location_id')::uuid;
      institution_ref := coalesce(
        (to_jsonb(NEW)->>'institution_id')::uuid,
        (to_jsonb(NEW)->>'managing_institution_id')::uuid,
        (to_jsonb(NEW)->>'owner_institution_id')::uuid
      );
      asset_ref := (to_jsonb(NEW)->>'asset_id')::uuid;
      IF unit_ref IS NOT NULL THEN
        SELECT institution_id INTO unit_institution FROM organizational_units WHERE id = unit_ref;
        IF unit_institution IS DISTINCT FROM institution_ref THEN
          RAISE EXCEPTION 'Organizational unit is incompatible with institution';
        END IF;
      END IF;
      IF TG_TABLE_NAME = 'public_assets' AND location_ref IS NOT NULL THEN
        SELECT institution_id INTO location_institution FROM asset_locations WHERE id = location_ref;
        asset_owner := (to_jsonb(NEW)->>'owner_institution_id')::uuid;
        asset_manager := (to_jsonb(NEW)->>'managing_institution_id')::uuid;
        IF location_institution NOT IN (asset_owner, coalesce(asset_manager, asset_owner)) THEN
          RAISE EXCEPTION 'Asset location is incompatible with institution';
        END IF;
      END IF;
      IF TG_TABLE_NAME IN ('asset_assignments','asset_disposals','asset_maintenance_records') THEN
        SELECT owner_institution_id, managing_institution_id INTO asset_owner, asset_manager
          FROM public_assets WHERE id = asset_ref;
        IF institution_ref NOT IN (asset_owner, coalesce(asset_manager, asset_owner)) THEN
          RAISE EXCEPTION 'Asset is incompatible with institution';
        END IF;
      END IF;
      RETURN NEW;
    END; $$ LANGUAGE plpgsql;
    CREATE TRIGGER trg_public_assets_institution BEFORE INSERT OR UPDATE ON public_assets
      FOR EACH ROW EXECUTE FUNCTION asset_institution_guard();
    CREATE TRIGGER trg_asset_locations_institution BEFORE INSERT OR UPDATE ON asset_locations
      FOR EACH ROW EXECUTE FUNCTION asset_institution_guard();
    CREATE TRIGGER trg_asset_assignments_institution BEFORE INSERT OR UPDATE ON asset_assignments
      FOR EACH ROW EXECUTE FUNCTION asset_institution_guard();
    CREATE TRIGGER trg_asset_disposals_institution BEFORE INSERT OR UPDATE ON asset_disposals
      FOR EACH ROW EXECUTE FUNCTION asset_institution_guard();
    CREATE TRIGGER trg_asset_maintenance_institution BEFORE INSERT OR UPDATE ON asset_maintenance_records
      FOR EACH ROW EXECUTE FUNCTION asset_institution_guard();
    """)
    op.execute("""
    CREATE FUNCTION asset_hierarchy_guard() RETURNS trigger AS $$
    DECLARE cyclic boolean; parent_ref uuid;
    BEGIN
      parent_ref := coalesce(
        (to_jsonb(NEW)->>'parent_id')::uuid,
        (to_jsonb(NEW)->>'parent_location_id')::uuid
      );
      IF TG_TABLE_NAME = 'asset_categories' AND parent_ref IS NOT NULL THEN
        WITH RECURSIVE ancestors(id) AS (
          SELECT parent_ref UNION ALL
          SELECT c.parent_id FROM asset_categories c JOIN ancestors a ON c.id = a.id
          WHERE c.parent_id IS NOT NULL
        ) SELECT EXISTS(SELECT 1 FROM ancestors WHERE id = NEW.id) INTO cyclic;
      ELSIF TG_TABLE_NAME = 'asset_locations' AND parent_ref IS NOT NULL THEN
        WITH RECURSIVE ancestors(id) AS (
          SELECT parent_ref UNION ALL
          SELECT l.parent_location_id FROM asset_locations l JOIN ancestors a ON l.id = a.id
          WHERE l.parent_location_id IS NOT NULL
        ) SELECT EXISTS(SELECT 1 FROM ancestors WHERE id = NEW.id) INTO cyclic;
      END IF;
      IF cyclic THEN RAISE EXCEPTION 'Asset hierarchy cycle is not allowed'; END IF;
      RETURN NEW;
    END; $$ LANGUAGE plpgsql;
    CREATE TRIGGER trg_asset_category_hierarchy BEFORE INSERT OR UPDATE ON asset_categories
      FOR EACH ROW EXECUTE FUNCTION asset_hierarchy_guard();
    CREATE TRIGGER trg_asset_location_hierarchy BEFORE INSERT OR UPDATE ON asset_locations
      FOR EACH ROW EXECUTE FUNCTION asset_hierarchy_guard();
    """)
    op.execute("""
    CREATE UNIQUE INDEX uq_active_asset_assignment ON asset_assignments(asset_id, assignment_type)
      WHERE status = 'active' AND end_date IS NULL;
    CREATE UNIQUE INDEX uq_active_asset_disposal ON asset_disposals(asset_id)
      WHERE status IN ('approved','effective','completed');
    CREATE FUNCTION asset_disposal_guard() RETURNS trigger AS $$
    BEGIN
      IF EXISTS (SELECT 1 FROM asset_assignments WHERE asset_id = NEW.asset_id
                 AND status = 'active' AND end_date IS NULL) THEN
        RAISE EXCEPTION 'Asset with active assignment cannot be disposed';
      END IF;
      RETURN NEW;
    END; $$ LANGUAGE plpgsql;
    CREATE TRIGGER trg_asset_disposal_active_assignment BEFORE INSERT OR UPDATE ON asset_disposals
      FOR EACH ROW EXECUTE FUNCTION asset_disposal_guard();
    """)


def downgrade() -> None:
    op.execute("DROP FUNCTION IF EXISTS asset_disposal_guard() CASCADE")
    op.execute("DROP FUNCTION IF EXISTS asset_hierarchy_guard() CASCADE")
    op.execute("DROP FUNCTION IF EXISTS asset_institution_guard() CASCADE")
    op.execute("DROP FUNCTION IF EXISTS public_asset_trace_guard() CASCADE")
    for name in reversed(TABLES):
        op.drop_table(name)
