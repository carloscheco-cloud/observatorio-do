"""Create public employment and versioned payroll domain.

Revision ID: 0005
Revises: 0004
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def enum(name: str, *values: str) -> sa.Enum:
    return sa.Enum(*values, name=name)


def upgrade() -> None:
    employment_type = enum(
        "employmenttype",
        "PERMANENT",
        "CAREER",
        "APPOINTED",
        "ELECTED",
        "TEMPORARY",
        "FIXED_TERM",
        "CONTRACTOR",
        "CONSULTANT",
        "MILITARY",
        "POLICE",
        "TEACHER",
        "HEALTH_WORKER",
        "INTERN",
        "HONORARY",
        "OTHER",
    )
    relationship_status = enum(
        "relationshipstatus", "PENDING", "ACTIVE", "SUSPENDED", "ENDED", "CANCELLED", "UNDER_REVIEW"
    )
    period_status = enum(
        "payrollperiodstatus",
        "DRAFT",
        "PROCESSED",
        "VALIDATED",
        "CONFIRMED",
        "REPLACED",
        "REJECTED",
    )
    entry_status = enum(
        "payrollentrystatus", "DRAFT", "NORMALIZED", "VALIDATED", "CONFIRMED", "REJECTED"
    )
    component_kind = enum("componentkind", "INCOME", "DEDUCTION")
    concept_code = enum(
        "payrollconceptcode",
        "BASE_SALARY",
        "REPRESENTATION_EXPENSE",
        "INCENTIVE",
        "BONUS",
        "OVERTIME",
        "PER_DIEM",
        "ALLOWANCE",
        "COMMISSION",
        "RETROACTIVE_PAYMENT",
        "SEVERANCE",
        "SOCIAL_SECURITY",
        "PENSION",
        "INCOME_TAX",
        "HEALTH_INSURANCE",
        "LOAN_DEDUCTION",
        "OTHER_INCOME",
        "OTHER_DEDUCTION",
    )
    version_action = enum(
        "payrollversionaction",
        "INITIAL",
        "CORRECTION",
        "REPLACEMENT",
        "CANCELLATION",
        "REPUBLICATION",
    )
    finding_severity = enum(
        "findingseverity", "INFORMATIONAL", "REVIEW_REQUIRED", "UNUSUAL", "HIGH_PRIORITY"
    )
    finding_status = enum("findingstatus", "OPEN", "REVIEWED", "DISMISSED", "RESOLVED")

    def timestamps() -> tuple[sa.Column[object], sa.Column[object]]:
        return (
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )

    op.create_table(
        "employment_relationships",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("person_id", sa.Uuid(), sa.ForeignKey("persons.id"), nullable=False),
        sa.Column("institution_id", sa.Uuid(), sa.ForeignKey("institutions.id"), nullable=False),
        sa.Column("position_id", sa.Uuid(), sa.ForeignKey("positions.id")),
        sa.Column("organizational_unit_id", sa.Uuid(), sa.ForeignKey("organizational_units.id")),
        sa.Column("employment_type", employment_type, nullable=False),
        sa.Column("relationship_status", relationship_status, nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date()),
        sa.Column("contract_reference", sa.String(300)),
        sa.Column("work_location", sa.Text()),
        sa.Column("territory_id", sa.Uuid(), sa.ForeignKey("territories.id")),
        sa.Column("source_id", sa.Uuid(), sa.ForeignKey("sources.id"), nullable=False),
        sa.Column("evidence_id", sa.Uuid(), sa.ForeignKey("evidence.id"), nullable=False),
        sa.Column("legal_basis_id", sa.Uuid(), sa.ForeignKey("legal_bases.id")),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}", nullable=False),
        *timestamps(),
        sa.CheckConstraint(
            "end_date IS NULL OR end_date >= start_date", name="ck_employment_dates"
        ),
    )
    op.create_table(
        "payroll_periods",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("institution_id", sa.Uuid(), sa.ForeignKey("institutions.id"), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("publication_date", sa.Date()),
        sa.Column("status", period_status, nullable=False),
        sa.Column("currency", sa.String(3), server_default="DOP", nullable=False),
        sa.Column("source_id", sa.Uuid(), sa.ForeignKey("sources.id")),
        sa.Column("evidence_id", sa.Uuid(), sa.ForeignKey("evidence.id")),
        sa.Column("record_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("reported_gross_total", sa.Numeric(18, 2)),
        sa.Column("calculated_gross_total", sa.Numeric(18, 2), server_default="0", nullable=False),
        sa.Column("calculated_net_total", sa.Numeric(18, 2), server_default="0", nullable=False),
        sa.Column("checksum", sa.String(64)),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.Column(
            "processed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("actor_type", sa.String(30), server_default="human", nullable=False),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}", nullable=False),
        *timestamps(),
        sa.UniqueConstraint(
            "institution_id", "year", "month", "version", name="uq_payroll_period_version"
        ),
        sa.CheckConstraint("month BETWEEN 1 AND 12", name="ck_payroll_month"),
        sa.CheckConstraint("period_end >= period_start", name="ck_payroll_period_dates"),
        sa.CheckConstraint(
            "record_count >= 0 AND calculated_gross_total >= 0 AND calculated_net_total >= 0 "
            "AND (reported_gross_total IS NULL OR reported_gross_total >= 0)",
            name="ck_payroll_period_amounts",
        ),
        sa.CheckConstraint(
            "status <> 'CONFIRMED' OR (source_id IS NOT NULL AND evidence_id IS NOT NULL)",
            name="ck_confirmed_period_traceability",
        ),
        sa.CheckConstraint(
            "checksum IS NULL OR checksum ~ '^[0-9a-f]{64}$'", name="ck_payroll_checksum"
        ),
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_canonical_payroll_month ON payroll_periods "
        "(institution_id, year, month) WHERE status = 'CONFIRMED'"
    )
    op.create_table(
        "payroll_versions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("previous_period_id", sa.Uuid(), sa.ForeignKey("payroll_periods.id")),
        sa.Column("new_period_id", sa.Uuid(), sa.ForeignKey("payroll_periods.id"), nullable=False),
        sa.Column("action", version_action, nullable=False),
        sa.Column("reason", sa.String(1000), nullable=False),
        sa.Column("effective_date", sa.Date(), nullable=False),
        sa.Column("source_id", sa.Uuid(), sa.ForeignKey("sources.id"), nullable=False),
        sa.Column("evidence_id", sa.Uuid(), sa.ForeignKey("evidence.id"), nullable=False),
        sa.Column("aggregate_differences", postgresql.JSONB(), server_default="{}", nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_table(
        "payroll_entries",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "payroll_period_id", sa.Uuid(), sa.ForeignKey("payroll_periods.id"), nullable=False
        ),
        sa.Column(
            "employment_relationship_id", sa.Uuid(), sa.ForeignKey("employment_relationships.id")
        ),
        sa.Column("person_id", sa.Uuid(), sa.ForeignKey("persons.id"), nullable=False),
        sa.Column("institution_id", sa.Uuid(), sa.ForeignKey("institutions.id"), nullable=False),
        sa.Column("position_id", sa.Uuid(), sa.ForeignKey("positions.id")),
        sa.Column("organizational_unit_id", sa.Uuid(), sa.ForeignKey("organizational_units.id")),
        sa.Column("employee_reference_hash", sa.String(64)),
        sa.Column("listed_name", sa.String(300), nullable=False),
        sa.Column("normalized_name", sa.String(300), nullable=False),
        sa.Column("employment_type", sa.String(50)),
        sa.Column("base_salary", sa.Numeric(18, 2), nullable=False),
        sa.Column("gross_income", sa.Numeric(18, 2), nullable=False),
        sa.Column("total_deductions", sa.Numeric(18, 2), nullable=False),
        sa.Column("net_income", sa.Numeric(18, 2), nullable=False),
        sa.Column("other_compensation", sa.Numeric(18, 2), server_default="0", nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("status", entry_status, nullable=False),
        sa.Column("source_id", sa.Uuid(), sa.ForeignKey("sources.id")),
        sa.Column("evidence_id", sa.Uuid(), sa.ForeignKey("evidence.id")),
        sa.Column("row_number", sa.Integer()),
        sa.Column("reconciliation_flag", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("raw_payload", postgresql.JSONB(), server_default="{}", nullable=False),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}", nullable=False),
        sa.Column(
            "processed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("actor_type", sa.String(30), server_default="human", nullable=False),
        *timestamps(),
        sa.UniqueConstraint(
            "payroll_period_id",
            "person_id",
            "position_id",
            "organizational_unit_id",
            name="uq_payroll_entry_canonical",
        ),
        sa.CheckConstraint(
            "base_salary >= 0 AND gross_income >= 0 AND total_deductions >= 0 "
            "AND net_income >= 0 AND other_compensation >= 0",
            name="ck_payroll_entry_amounts",
        ),
        sa.CheckConstraint(
            "status <> 'CONFIRMED' OR (source_id IS NOT NULL AND evidence_id IS NOT NULL)",
            name="ck_confirmed_entry_traceability",
        ),
        sa.CheckConstraint(
            "employee_reference_hash IS NULL OR employee_reference_hash ~ '^[0-9a-f]{64}$'",
            name="ck_employee_reference_hash",
        ),
    )
    op.create_table(
        "payroll_concepts",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("code", concept_code, unique=True, nullable=False),
        sa.Column("kind", component_kind, nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}"),
    )
    op.create_table(
        "payroll_entry_components",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "payroll_entry_id", sa.Uuid(), sa.ForeignKey("payroll_entries.id"), nullable=False
        ),
        sa.Column("concept_id", sa.Uuid(), sa.ForeignKey("payroll_concepts.id"), nullable=False),
        sa.Column("kind", component_kind, nullable=False),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("source_id", sa.Uuid(), sa.ForeignKey("sources.id"), nullable=False),
        sa.Column("evidence_id", sa.Uuid(), sa.ForeignKey("evidence.id"), nullable=False),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("amount >= 0", name="ck_payroll_component_amount"),
    )
    op.create_table(
        "payroll_findings",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("finding_type", sa.String(100), nullable=False),
        sa.Column("severity", finding_severity, nullable=False),
        sa.Column("person_id", sa.Uuid(), sa.ForeignKey("persons.id")),
        sa.Column("institution_id", sa.Uuid(), sa.ForeignKey("institutions.id"), nullable=False),
        sa.Column(
            "payroll_period_id", sa.Uuid(), sa.ForeignKey("payroll_periods.id"), nullable=False
        ),
        sa.Column("comparison_period_id", sa.Uuid(), sa.ForeignKey("payroll_periods.id")),
        sa.Column("observed_value", postgresql.JSONB(), server_default="{}", nullable=False),
        sa.Column(
            "expected_or_previous_value", postgresql.JSONB(), server_default="{}", nullable=False
        ),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("evidence_id", sa.Uuid(), sa.ForeignKey("evidence.id")),
        sa.Column("status", finding_status, server_default="OPEN", nullable=False),
        sa.Column("reviewer_notes", sa.Text()),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )

    indexes = {
        "employment_relationships": (
            "person_id",
            "institution_id",
            "position_id",
            "organizational_unit_id",
            "relationship_status",
            "employment_type",
            "start_date",
            "end_date",
        ),
        "payroll_periods": (
            "institution_id",
            "year",
            "month",
            "period_start",
            "period_end",
            "status",
            "checksum",
        ),
        "payroll_entries": (
            "payroll_period_id",
            "employment_relationship_id",
            "person_id",
            "institution_id",
            "position_id",
            "organizational_unit_id",
            "status",
            "employment_type",
            "normalized_name",
            "employee_reference_hash",
        ),
        "payroll_findings": (
            "finding_type",
            "severity",
            "institution_id",
            "payroll_period_id",
            "comparison_period_id",
        ),
    }
    for table, columns in indexes.items():
        for column in columns:
            op.create_index(f"ix_{table}_{column}", table, [column])
    op.create_index(
        "ix_payroll_period_compare",
        "payroll_periods",
        ["institution_id", "year", "month", "version"],
    )

    op.execute(r"""
    CREATE FUNCTION validate_block5_integrity() RETURNS trigger AS $$
    DECLARE target_institution uuid; ref_institution uuid; evidence_source uuid;
    BEGIN
      IF TG_TABLE_NAME = 'employment_relationships' THEN
        target_institution := NEW.institution_id;
      ELSE
        SELECT institution_id INTO target_institution
          FROM payroll_periods WHERE id = NEW.payroll_period_id;
        IF target_institution IS DISTINCT FROM NEW.institution_id THEN
          RAISE EXCEPTION 'Entry institution must match payroll period';
        END IF;
      END IF;
      IF NEW.position_id IS NOT NULL THEN
        SELECT institution_id INTO ref_institution FROM positions WHERE id = NEW.position_id;
        IF ref_institution IS DISTINCT FROM target_institution THEN
          RAISE EXCEPTION 'Position institution mismatch';
        END IF;
      END IF;
      IF NEW.organizational_unit_id IS NOT NULL THEN
        SELECT institution_id INTO ref_institution
          FROM organizational_units WHERE id = NEW.organizational_unit_id;
        IF ref_institution IS DISTINCT FROM target_institution THEN
          RAISE EXCEPTION 'Unit institution mismatch';
        END IF;
      END IF;
      SELECT source_id INTO evidence_source FROM evidence WHERE id = NEW.evidence_id;
      IF NEW.evidence_id IS NOT NULL AND evidence_source IS DISTINCT FROM NEW.source_id THEN
        RAISE EXCEPTION 'Source must match evidence source';
      END IF;
      IF TG_TABLE_NAME = 'payroll_entries' AND (
        NEW.listed_name ~ '\m[0-9]{3}-?[0-9]{7}-?[0-9]\M'
        OR NEW.normalized_name ~ '\m[0-9]{3}-?[0-9]{7}-?[0-9]\M'
        OR NEW.raw_payload::text ~ '[0-9]{3}-?[0-9]{7}-?[0-9]'
      ) THEN RAISE EXCEPTION 'Apparent national identifier is prohibited'; END IF;
      RETURN NEW;
    END; $$ LANGUAGE plpgsql;
    CREATE TRIGGER employment_relationships_validate
      BEFORE INSERT OR UPDATE ON employment_relationships
      FOR EACH ROW EXECUTE FUNCTION validate_block5_integrity();
    CREATE TRIGGER payroll_entries_validate BEFORE INSERT OR UPDATE ON payroll_entries
      FOR EACH ROW EXECUTE FUNCTION validate_block5_integrity();

    CREATE FUNCTION validate_payroll_traceability() RETURNS trigger AS $$
    DECLARE evidence_source uuid;
    BEGIN
      IF NEW.evidence_id IS NOT NULL THEN
        SELECT source_id INTO evidence_source FROM evidence WHERE id = NEW.evidence_id;
        IF evidence_source IS DISTINCT FROM NEW.source_id THEN
          RAISE EXCEPTION 'Source must match evidence source';
        END IF;
      END IF;
      RETURN NEW;
    END; $$ LANGUAGE plpgsql;
    CREATE TRIGGER payroll_periods_traceability BEFORE INSERT OR UPDATE ON payroll_periods
      FOR EACH ROW EXECUTE FUNCTION validate_payroll_traceability();
    CREATE TRIGGER payroll_components_traceability
      BEFORE INSERT OR UPDATE ON payroll_entry_components
      FOR EACH ROW EXECUTE FUNCTION validate_payroll_traceability();

    CREATE FUNCTION prevent_confirmed_payroll_overwrite() RETURNS trigger AS $$
    BEGIN
      IF OLD.status = 'CONFIRMED' AND ROW(OLD.*) IS DISTINCT FROM ROW(NEW.*) THEN
        RAISE EXCEPTION 'Confirmed payroll cannot be overwritten; create a new version';
      END IF;
      RETURN NEW;
    END; $$ LANGUAGE plpgsql;
    CREATE TRIGGER payroll_periods_no_silent_overwrite BEFORE UPDATE ON payroll_periods
      FOR EACH ROW EXECUTE FUNCTION prevent_confirmed_payroll_overwrite();
    """)
    for table in (
        "employment_relationships",
        "payroll_periods",
        "payroll_versions",
        "payroll_entries",
        "payroll_concepts",
        "payroll_entry_components",
    ):
        op.execute(
            f"CREATE TRIGGER {table}_reject_ai BEFORE INSERT OR UPDATE OR DELETE ON {table} "
            "FOR EACH ROW EXECUTE FUNCTION reject_ai_canonical_write()"
        )


def downgrade() -> None:
    op.execute("DROP FUNCTION IF EXISTS prevent_confirmed_payroll_overwrite() CASCADE")
    op.execute("DROP FUNCTION IF EXISTS validate_payroll_traceability() CASCADE")
    op.execute("DROP FUNCTION IF EXISTS validate_block5_integrity() CASCADE")
    for table in (
        "payroll_findings",
        "payroll_entry_components",
        "payroll_concepts",
        "payroll_entries",
        "payroll_versions",
        "payroll_periods",
        "employment_relationships",
    ):
        op.drop_table(table)
    for name in (
        "findingstatus",
        "findingseverity",
        "payrollversionaction",
        "payrollconceptcode",
        "componentkind",
        "payrollentrystatus",
        "payrollperiodstatus",
        "relationshipstatus",
        "employmenttype",
    ):
        sa.Enum(name=name).drop(op.get_bind(), checkfirst=True)
