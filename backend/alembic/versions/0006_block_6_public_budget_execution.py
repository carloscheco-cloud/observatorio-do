"""Create public budget, revenue and financial execution domain.

Revision ID: 0006
Revises: 0005
"""

from collections.abc import Sequence

from alembic import op
from app.modules.budget.models import Base

revision: str = "0006"
down_revision: str | None = "0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TABLES = (
    "budget_cycles",
    "budget_classifiers",
    "funding_sources",
    "financing_organizations",
    "budget_programs",
    "budget_appropriations",
    "budget_modifications",
    "budget_execution_records",
    "budget_revenues",
    "interinstitutional_transfers",
    "budget_versions",
    "budget_findings",
)


def upgrade() -> None:
    bind = op.get_bind()
    for table in Base.metadata.sorted_tables:
        if table.name in TABLES:
            table.create(bind, checkfirst=True)

    checks = {
        "budget_cycles": (
            "ck_budget_cycle_dates CHECK (end_date >= start_date)",
            "ck_budget_cycle_trace CHECK (status <> 'CONFIRMED' OR "
            "(source_id IS NOT NULL AND evidence_id IS NOT NULL AND legal_basis_id IS NOT NULL))",
        ),
        "budget_classifiers": (
            "ck_classifier_dates CHECK (valid_to IS NULL OR valid_to >= valid_from)",
            "ck_classifier_trace CHECK (status <> 'CONFIRMED' OR "
            "(source_id IS NOT NULL AND evidence_id IS NOT NULL))",
        ),
        "budget_programs": (
            "ck_budget_program_dates CHECK (end_date IS NULL OR end_date >= start_date)",
        ),
        "budget_appropriations": (
            "ck_appropriation_amounts CHECK (approved_amount >= 0 AND "
            "(current_amount IS NULL OR current_amount >= 0))",
            "ck_appropriation_trace CHECK (status <> 'CONFIRMED' OR "
            "(current_amount IS NOT NULL AND source_id IS NOT NULL AND evidence_id IS NOT NULL))",
        ),
        "budget_modifications": (
            "ck_modification_amount CHECK (amount > 0 AND previous_balance >= 0 "
            "AND resulting_balance >= 0)",
            "ck_modification_transfer CHECK (source_appropriation_id IS NULL OR "
            "destination_appropriation_id IS NULL OR "
            "source_appropriation_id <> destination_appropriation_id)",
            "ck_modification_trace CHECK (status <> 'CONFIRMED' OR "
            "(legal_basis_id IS NOT NULL AND source_id IS NOT NULL AND evidence_id IS NOT NULL))",
        ),
        "budget_execution_records": (
            "ck_execution_dates CHECK (period_end >= period_start)",
            "ck_execution_amounts CHECK (initial_budget >= 0 AND current_budget >= 0 AND "
            "committed_amount >= 0 AND accrued_amount >= 0 AND paid_amount >= 0 "
            "AND available_balance >= 0)",
            "ck_execution_sequence CHECK (exception_documented OR "
            "(paid_amount <= accrued_amount AND accrued_amount <= committed_amount))",
            "ck_execution_trace CHECK (status <> 'CONFIRMED' OR "
            "(source_id IS NOT NULL AND evidence_id IS NOT NULL))",
        ),
        "budget_revenues": (
            "ck_revenue_dates CHECK (period_end >= period_start)",
            "ck_revenue_amounts CHECK (estimated_amount >= 0 AND modified_estimate >= 0 "
            "AND collected_amount >= 0 AND (accrued_amount IS NULL OR accrued_amount >= 0))",
        ),
        "interinstitutional_transfers": (
            "ck_transfer_amount CHECK (amount > 0 AND paid_amount >= 0)",
            "ck_transfer_parties CHECK (origin_institution_id <> destination_institution_id)",
        ),
    }
    for table, constraints in checks.items():
        for constraint in constraints:
            op.execute(f"ALTER TABLE {table} ADD CONSTRAINT {constraint}")

    op.execute(
        "CREATE UNIQUE INDEX uq_active_budget_cycle ON budget_cycles "
        "(fiscal_year, jurisdiction, government_level, cycle_type) "
        "WHERE status IN ('CONFIRMED', 'CLOSED')"
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_budget_classifier_version ON budget_classifiers "
        "(classifier_type, code, valid_from)"
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_budget_appropriation_canonical ON budget_appropriations "
        "(budget_cycle_id, institution_id, COALESCE(program_id, "
        "'00000000-0000-0000-0000-000000000000'), "
        "classifier_id, COALESCE(funding_source_id, '00000000-0000-0000-0000-000000000000'), "
        "valid_from, version) WHERE status = 'CONFIRMED'"
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_execution_period ON budget_execution_records "
        "(appropriation_id, period_start, period_end, version) WHERE status = 'CONFIRMED'"
    )
    indexes = {
        "budget_cycles": ("fiscal_year", "status", "checksum", "start_date", "end_date"),
        "budget_classifiers": ("status", "parent_id", "valid_from", "valid_to"),
        "budget_programs": (
            "institution_id",
            "budget_cycle_id",
            "parent_id",
            "organizational_unit_id",
            "territory_id",
            "status",
        ),
        "budget_appropriations": (
            "institution_id",
            "budget_cycle_id",
            "program_id",
            "organizational_unit_id",
            "territory_id",
            "classifier_id",
            "funding_source_id",
            "status",
            "checksum",
        ),
        "budget_execution_records": (
            "institution_id",
            "budget_cycle_id",
            "appropriation_id",
            "execution_period",
            "period_start",
            "period_end",
            "status",
            "checksum",
        ),
        "budget_findings": (
            "finding_type",
            "severity",
            "institution_id",
            "budget_cycle_id",
            "appropriation_id",
        ),
    }
    for table, columns in indexes.items():
        for column in columns:
            op.create_index(f"ix_{table}_{column}", table, [column])

    op.execute("""
    CREATE FUNCTION validate_budget_integrity() RETURNS trigger AS $$
    DECLARE ref_institution uuid; ref_cycle uuid; evidence_source uuid;
    BEGIN
      IF NEW.evidence_id IS NOT NULL THEN
        SELECT source_id INTO evidence_source FROM evidence WHERE id = NEW.evidence_id;
        IF evidence_source IS DISTINCT FROM NEW.source_id THEN
          RAISE EXCEPTION 'Source must match evidence source';
        END IF;
      END IF;
      IF TG_TABLE_NAME = 'budget_execution_records' THEN
        SELECT institution_id, budget_cycle_id INTO ref_institution, ref_cycle
          FROM budget_appropriations WHERE id = NEW.appropriation_id;
        IF ref_institution IS DISTINCT FROM NEW.institution_id
           OR ref_cycle IS DISTINCT FROM NEW.budget_cycle_id THEN
          RAISE EXCEPTION 'Execution appropriation is incompatible';
        END IF;
      END IF;
      IF TG_TABLE_NAME IN ('budget_appropriations','budget_programs') THEN
        IF NEW.organizational_unit_id IS NOT NULL THEN
          SELECT institution_id INTO ref_institution FROM organizational_units
            WHERE id = NEW.organizational_unit_id;
          IF ref_institution IS DISTINCT FROM NEW.institution_id THEN
            RAISE EXCEPTION 'Budget unit institution mismatch';
          END IF;
        END IF;
      END IF;
      RETURN NEW;
    END; $$ LANGUAGE plpgsql;
    """)
    for table in (
        "budget_cycles",
        "budget_classifiers",
        "funding_sources",
        "financing_organizations",
        "budget_programs",
        "budget_appropriations",
        "budget_modifications",
        "budget_execution_records",
        "budget_revenues",
        "interinstitutional_transfers",
        "budget_versions",
    ):
        op.execute(
            f"CREATE TRIGGER {table}_integrity BEFORE INSERT OR UPDATE ON {table} "
            "FOR EACH ROW EXECUTE FUNCTION validate_budget_integrity()"
        )
        op.execute(
            f"CREATE TRIGGER {table}_reject_ai BEFORE INSERT OR UPDATE OR DELETE ON {table} "
            "FOR EACH ROW EXECUTE FUNCTION reject_ai_canonical_write()"
        )
    op.execute("""
    CREATE FUNCTION prevent_confirmed_budget_overwrite() RETURNS trigger AS $$
    BEGIN
      IF OLD.status = 'CONFIRMED' AND ROW(OLD.*) IS DISTINCT FROM ROW(NEW.*) THEN
        RAISE EXCEPTION 'Confirmed budget cannot be overwritten; create a new version';
      END IF;
      RETURN NEW;
    END; $$ LANGUAGE plpgsql;
    CREATE TRIGGER budget_cycles_no_overwrite BEFORE UPDATE ON budget_cycles
      FOR EACH ROW EXECUTE FUNCTION prevent_confirmed_budget_overwrite();
    CREATE TRIGGER appropriations_no_overwrite BEFORE UPDATE ON budget_appropriations
      FOR EACH ROW EXECUTE FUNCTION prevent_confirmed_budget_overwrite();
    """)


def downgrade() -> None:
    op.execute("DROP FUNCTION IF EXISTS prevent_confirmed_budget_overwrite() CASCADE")
    op.execute("DROP FUNCTION IF EXISTS validate_budget_integrity() CASCADE")
    bind = op.get_bind()
    for name in reversed(TABLES):
        Base.metadata.tables[name].drop(bind, checkfirst=True)
    op.execute("DROP TYPE IF EXISTS cycletype")
    op.execute("DROP TYPE IF EXISTS budgetstatus")
