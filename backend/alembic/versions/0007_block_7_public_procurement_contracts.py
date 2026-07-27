"""Create public procurement, suppliers and contractual execution.

Revision ID: 0007
Revises: 0006
"""

from collections.abc import Sequence

from alembic import op
from app.db.base import Base
from app.modules.procurement_processes import models as procurement_models  # noqa: F401
from app.modules.suppliers import models as supplier_models  # noqa: F401

revision: str = "0007"
down_revision: str | None = "0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TABLES = (
    "suppliers",
    "supplier_history",
    "procurement_processes",
    "procurement_lots",
    "procurement_items",
    "procurement_bids",
    "procurement_evaluations",
    "procurement_awards",
    "procurement_contracts",
    "contract_amendments",
    "purchase_orders",
    "contract_deliveries",
    "contract_payments",
    "contract_guarantees",
    "procurement_challenges",
    "procurement_versions",
    "procurement_findings",
)

CANONICAL = (
    "suppliers",
    "procurement_processes",
    "procurement_lots",
    "procurement_items",
    "procurement_bids",
    "procurement_evaluations",
    "procurement_awards",
    "procurement_contracts",
    "contract_amendments",
    "purchase_orders",
    "contract_deliveries",
    "contract_payments",
    "contract_guarantees",
    "procurement_challenges",
    "procurement_versions",
)


def upgrade() -> None:
    bind = op.get_bind()
    for table in Base.metadata.sorted_tables:
        if table.name in TABLES:
            table.create(bind, checkfirst=True)

    checks = {
        "procurement_processes": (
            "ck_procurement_process_amount CHECK (estimated_amount >= 0)",
            "ck_procurement_process_dates CHECK "
            "(submission_deadline IS NULL OR publication_date IS NULL OR "
            "submission_deadline >= publication_date)",
            "ck_procurement_opening_date CHECK "
            "(opening_date IS NULL OR submission_deadline IS NULL OR "
            "opening_date >= submission_deadline)",
            "ck_procurement_currency CHECK (currency ~ '^[A-Z]{3}$')",
        ),
        "procurement_lots": (
            "ck_procurement_lot_amounts CHECK (estimated_amount >= 0 AND "
            "(awarded_amount IS NULL OR awarded_amount >= 0))",
        ),
        "procurement_items": (
            "ck_procurement_item_amounts CHECK (quantity >= 0 AND estimated_total >= 0 AND "
            "(awarded_total IS NULL OR awarded_total >= 0) AND "
            "(estimated_unit_price IS NULL OR estimated_unit_price >= 0) AND "
            "(awarded_unit_price IS NULL OR awarded_unit_price >= 0))",
        ),
        "procurement_bids": (
            "ck_procurement_bid_amount CHECK (offered_amount >= 0)",
            "ck_procurement_bid_scores CHECK "
            "((technical_score IS NULL OR technical_score BETWEEN 0 AND 100) AND "
            "(financial_score IS NULL OR financial_score BETWEEN 0 AND 100) AND "
            "(total_score IS NULL OR total_score BETWEEN 0 AND 100))",
        ),
        "procurement_evaluations": (
            "ck_procurement_evaluation_score CHECK (score IS NULL OR "
            "(score >= 0 AND maximum_score IS NOT NULL AND score <= maximum_score))",
        ),
        "procurement_awards": ("ck_procurement_award_amount CHECK (awarded_amount >= 0)",),
        "procurement_contracts": (
            "ck_procurement_contract_dates CHECK "
            "(signature_date <= start_date AND start_date <= end_date)",
            "ck_procurement_contract_amounts CHECK (original_amount >= 0 AND current_amount >= 0 "
            "AND paid_amount >= 0 AND (exception_documented OR paid_amount <= current_amount))",
        ),
        "contract_amendments": (
            "ck_contract_amendment_amounts CHECK (previous_amount >= 0 AND new_amount >= 0)",
            "ck_contract_amendment_trace CHECK "
            "(status <> 'confirmed' OR legal_basis_id IS NOT NULL)",
        ),
        "purchase_orders": ("ck_purchase_order_amount CHECK (amount >= 0)",),
        "contract_deliveries": (
            "ck_contract_delivery_dates CHECK "
            "(acceptance_date IS NULL OR acceptance_date >= delivery_date)",
            "ck_contract_delivery_amounts CHECK "
            "((delivered_amount IS NULL OR delivered_amount >= 0) AND "
            "(accepted_amount IS NULL OR accepted_amount >= 0))",
        ),
        "contract_payments": (
            "ck_contract_payment_amounts CHECK (gross_amount >= 0 AND deductions >= 0 "
            "AND net_amount >= 0 AND net_amount = gross_amount - deductions)",
        ),
        "contract_guarantees": (
            "ck_contract_guarantee_amount CHECK (amount >= 0)",
            "ck_contract_guarantee_dates CHECK (expiration_date >= issue_date)",
            "ck_contract_guarantee_target CHECK "
            "(procurement_process_id IS NOT NULL OR contract_id IS NOT NULL)",
        ),
        "procurement_challenges": (
            "ck_procurement_challenge_dates CHECK "
            "(decision_date IS NULL OR decision_date >= filing_date)",
        ),
    }
    for table, constraints in checks.items():
        for constraint in constraints:
            op.execute(f"ALTER TABLE {table} ADD CONSTRAINT {constraint}")

    op.execute(
        "CREATE UNIQUE INDEX uq_procurement_process_code "
        "ON procurement_processes (institution_id, source_id, process_code)"
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_procurement_contract_code "
        "ON procurement_contracts (institution_id, source_id, contract_code, version)"
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_procurement_lot_number "
        "ON procurement_lots (procurement_process_id, lot_number)"
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_procurement_active_lot_award ON procurement_awards (lot_id) "
        "WHERE lot_id IS NOT NULL AND award_status IN "
        "('confirmed','partially_executed','completed')"
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_procurement_payment_reference "
        "ON contract_payments (contract_id, source_id, payment_reference)"
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_procurement_amendment_number "
        "ON contract_amendments (contract_id, amendment_number)"
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_supplier_reference_hash ON suppliers (registry_reference_hash) "
        "WHERE registry_reference_hash IS NOT NULL"
    )

    indexes = {
        "suppliers": ("normalized_name", "territory_id", "registry_reference_hash"),
        "supplier_history": ("supplier_id", "effective_date"),
        "procurement_processes": (
            "institution_id",
            "organizational_unit_id",
            "territory_id",
            "process_code",
            "publication_date",
            "process_status",
            "procedure_type",
            "procurement_type",
            "fiscal_year",
            "checksum",
        ),
        "procurement_lots": ("procurement_process_id",),
        "procurement_items": ("procurement_process_id", "lot_id", "classification_code"),
        "procurement_bids": ("procurement_process_id", "lot_id", "supplier_id"),
        "procurement_evaluations": ("procurement_process_id", "bid_id", "supplier_id"),
        "procurement_awards": (
            "procurement_process_id",
            "lot_id",
            "supplier_id",
            "bid_id",
            "award_date",
        ),
        "procurement_contracts": (
            "procurement_process_id",
            "award_id",
            "institution_id",
            "supplier_id",
            "contract_code",
            "signature_date",
            "start_date",
            "end_date",
            "contract_status",
            "checksum",
        ),
        "contract_amendments": ("contract_id", "effective_date"),
        "purchase_orders": ("contract_id",),
        "contract_deliveries": ("contract_id", "purchase_order_id"),
        "contract_payments": ("contract_id", "institution_id", "supplier_id", "payment_date"),
        "contract_guarantees": ("procurement_process_id", "contract_id", "supplier_id"),
        "procurement_challenges": ("procurement_process_id", "supplier_id"),
        "procurement_versions": ("entity_type", "new_entity_id", "effective_date", "checksum"),
        "procurement_findings": (
            "finding_type",
            "severity",
            "institution_id",
            "procurement_process_id",
            "contract_id",
            "supplier_id",
        ),
    }
    for table, columns in indexes.items():
        for column in columns:
            op.create_index(f"ix_{table}_{column}", table, [column])

    op.execute("""
    CREATE FUNCTION validate_procurement_integrity() RETURNS trigger AS $$
    DECLARE
      evidence_source uuid; ref_process uuid; ref_supplier uuid; ref_institution uuid;
      ref_lot uuid; ref_currency varchar(3); contract_amount numeric; payments numeric;
    BEGIN
      IF NEW.evidence_id IS NULL OR NEW.source_id IS NULL THEN
        RAISE EXCEPTION 'Canonical procurement data requires source and evidence';
      END IF;
      SELECT source_id INTO evidence_source FROM evidence WHERE id = NEW.evidence_id;
      IF evidence_source IS DISTINCT FROM NEW.source_id THEN
        RAISE EXCEPTION 'Source must match evidence source';
      END IF;
      IF TG_TABLE_NAME IN ('procurement_items','procurement_bids','procurement_awards') THEN
        IF NEW.lot_id IS NOT NULL THEN
          SELECT procurement_process_id INTO ref_process
            FROM procurement_lots WHERE id = NEW.lot_id;
          IF ref_process IS DISTINCT FROM NEW.procurement_process_id THEN
            RAISE EXCEPTION 'Lot belongs to another procurement process';
          END IF;
        END IF;
      END IF;
      IF TG_TABLE_NAME = 'procurement_awards' AND NEW.bid_id IS NOT NULL THEN
        SELECT procurement_process_id, supplier_id, lot_id
          INTO ref_process, ref_supplier, ref_lot FROM procurement_bids WHERE id = NEW.bid_id;
        IF ref_process IS DISTINCT FROM NEW.procurement_process_id
           OR ref_supplier IS DISTINCT FROM NEW.supplier_id
           OR ref_lot IS DISTINCT FROM NEW.lot_id THEN
          RAISE EXCEPTION 'Award is incompatible with bid';
        END IF;
      END IF;
      IF TG_TABLE_NAME = 'procurement_contracts' THEN
        SELECT p.institution_id, a.procurement_process_id, a.supplier_id
          INTO ref_institution, ref_process, ref_supplier
          FROM procurement_awards a JOIN procurement_processes p ON p.id = a.procurement_process_id
          WHERE a.id = NEW.award_id;
        IF ref_process IS DISTINCT FROM NEW.procurement_process_id
           OR ref_institution IS DISTINCT FROM NEW.institution_id
           OR ref_supplier IS DISTINCT FROM NEW.supplier_id THEN
          RAISE EXCEPTION 'Contract is incompatible with award';
        END IF;
      END IF;
      IF TG_TABLE_NAME = 'contract_payments' THEN
        SELECT institution_id, supplier_id, currency, current_amount
          INTO ref_institution, ref_supplier, ref_currency, contract_amount
          FROM procurement_contracts WHERE id = NEW.contract_id;
        IF ref_institution IS DISTINCT FROM NEW.institution_id
           OR ref_supplier IS DISTINCT FROM NEW.supplier_id
           OR ref_currency IS DISTINCT FROM NEW.currency THEN
          RAISE EXCEPTION 'Payment is incompatible with contract';
        END IF;
        SELECT COALESCE(sum(net_amount), 0) INTO payments FROM contract_payments
          WHERE contract_id = NEW.contract_id AND id IS DISTINCT FROM NEW.id;
        IF NOT NEW.exception_documented AND payments + NEW.net_amount > contract_amount THEN
          RAISE EXCEPTION 'Accumulated payments exceed contract amount';
        END IF;
      END IF;
      RETURN NEW;
    END; $$ LANGUAGE plpgsql;
    """)
    for table in CANONICAL:
        op.execute(
            f"CREATE TRIGGER {table}_integrity BEFORE INSERT OR UPDATE ON {table} "
            "FOR EACH ROW EXECUTE FUNCTION validate_procurement_integrity()"
        )
        op.execute(
            f"CREATE TRIGGER {table}_reject_ai BEFORE INSERT OR UPDATE OR DELETE ON {table} "
            "FOR EACH ROW EXECUTE FUNCTION reject_ai_canonical_write()"
        )

    op.execute("""
    CREATE FUNCTION prevent_confirmed_procurement_overwrite() RETURNS trigger AS $$
    BEGIN
      IF OLD.validation_status = 'confirmed' AND ROW(OLD.*) IS DISTINCT FROM ROW(NEW.*) THEN
        RAISE EXCEPTION 'Confirmed procurement record cannot be overwritten; create a version';
      END IF;
      RETURN NEW;
    END; $$ LANGUAGE plpgsql;
    CREATE TRIGGER procurement_processes_no_overwrite BEFORE UPDATE ON procurement_processes
      FOR EACH ROW EXECUTE FUNCTION prevent_confirmed_procurement_overwrite();
    CREATE TRIGGER procurement_awards_no_overwrite BEFORE UPDATE ON procurement_awards
      FOR EACH ROW EXECUTE FUNCTION prevent_confirmed_procurement_overwrite();
    CREATE TRIGGER procurement_contracts_no_overwrite BEFORE UPDATE ON procurement_contracts
      FOR EACH ROW EXECUTE FUNCTION prevent_confirmed_procurement_overwrite();
    """)


def downgrade() -> None:
    op.execute("DROP FUNCTION IF EXISTS prevent_confirmed_procurement_overwrite() CASCADE")
    op.execute("DROP FUNCTION IF EXISTS validate_procurement_integrity() CASCADE")
    bind = op.get_bind()
    for name in reversed(TABLES):
        Base.metadata.tables[name].drop(bind, checkfirst=True)
    op.execute("DROP TYPE IF EXISTS procurementtype")
    op.execute("DROP TYPE IF EXISTS proceduretype")
    op.execute("DROP TYPE IF EXISTS processstatus")
    op.execute("DROP TYPE IF EXISTS suppliertype")
