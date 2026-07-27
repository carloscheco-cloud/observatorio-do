# ruff: noqa: E501
"""Block 8: public debt, obligations, transfers and fiscal risks.

Revision ID: 0008
Revises: 0007
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0008"
down_revision: str | None = "0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TABLES = (
    "creditors",
    "creditor_history",
    "debt_instruments",
    "debt_terms",
    "debt_disbursements",
    "debt_service_schedules",
    "debt_payments",
    "debt_balance_snapshots",
    "debt_issuances",
    "public_guarantees",
    "guarantee_events",
    "public_obligations",
    "financial_transfers",
    "public_subsidies",
    "multi_year_commitments",
    "debt_restructuring_events",
    "debt_versions",
    "fiscal_risk_findings",
)


def upgrade() -> None:
    from app.db.base import Base
    from app.modules import models  # noqa: F401

    bind = op.get_bind()
    for name in TABLES:
        Base.metadata.tables[name].create(bind=bind)

    constraints = {
        "creditors": [
            "CONSTRAINT ck_creditor_hash CHECK (registry_reference_hash IS NULL OR registry_reference_hash ~ '^[0-9a-f]{64}$')",
        ],
        "debt_instruments": [
            "CONSTRAINT ck_debt_amounts CHECK (original_principal >= 0 AND current_principal >= 0 AND (approved_amount IS NULL OR approved_amount >= 0))",
            "CONSTRAINT ck_debt_dates CHECK (maturity_date IS NULL OR maturity_date >= effective_date)",
            "CONSTRAINT ck_debt_principal CHECK (current_principal <= original_principal OR exception_documented)",
            "CONSTRAINT ck_debt_currency CHECK (currency ~ '^[A-Z]{3}$')",
        ],
        "debt_terms": [
            "CONSTRAINT ck_term_dates CHECK (valid_to IS NULL OR valid_to >= valid_from)",
            "CONSTRAINT ck_term_rates CHECK (coalesce(nominal_rate,0) BETWEEN 0 AND 1000 AND coalesce(reference_rate_value,0) BETWEEN 0 AND 1000 AND coalesce(spread_rate,0) BETWEEN 0 AND 1000 AND coalesce(penalty_rate,0) BETWEEN 0 AND 1000)",
        ],
        "debt_disbursements": ["CONSTRAINT ck_disbursement_amount CHECK (amount > 0)"],
        "debt_service_schedules": [
            "CONSTRAINT ck_schedule_amounts CHECK (principal_due >= 0 AND interest_due >= 0 AND fees_due >= 0 AND penalties_due >= 0)",
            "CONSTRAINT ck_schedule_total CHECK (total_due = principal_due + interest_due + fees_due + penalties_due)",
            "CONSTRAINT uq_schedule_installment UNIQUE (debt_instrument_id, installment_number)",
        ],
        "debt_payments": [
            "CONSTRAINT ck_payment_amounts CHECK (principal_paid >= 0 AND interest_paid >= 0 AND fees_paid >= 0 AND penalties_paid >= 0)",
            "CONSTRAINT ck_payment_total CHECK (total_paid = principal_paid + interest_paid + fees_paid + penalties_paid)",
            "CONSTRAINT uq_debt_payment UNIQUE (debt_instrument_id, payment_reference)",
        ],
        "debt_balance_snapshots": [
            "CONSTRAINT ck_balance_amounts CHECK (principal_outstanding >= 0 AND interest_accrued >= 0 AND arrears_principal >= 0 AND arrears_interest >= 0 AND fees_outstanding >= 0)",
            "CONSTRAINT ck_balance_total CHECK (total_outstanding = principal_outstanding + interest_accrued + arrears_principal + arrears_interest + fees_outstanding)",
            "CONSTRAINT uq_balance_version UNIQUE (debt_instrument_id, snapshot_date, version)",
        ],
        "public_guarantees": [
            "CONSTRAINT ck_guarantee_entities CHECK (guarantor_institution_id <> guaranteed_entity_id OR exception_documented)",
            "CONSTRAINT ck_guarantee_amounts CHECK (guaranteed_amount >= 0 AND outstanding_exposure >= 0 AND (outstanding_exposure <= guaranteed_amount OR exception_documented))",
        ],
        "guarantee_events": ["CONSTRAINT ck_guarantee_event_amount CHECK (amount >= 0)"],
        "public_obligations": [
            "CONSTRAINT ck_obligation_amounts CHECK (original_amount >= 0 AND outstanding_amount >= 0 AND paid_amount >= 0 AND original_amount = outstanding_amount + paid_amount)",
        ],
        "financial_transfers": [
            "CONSTRAINT ck_transfer_entities CHECK (origin_institution_id <> destination_institution_id)",
            "CONSTRAINT ck_transfer_amounts CHECK (approved_amount >= 0 AND paid_amount >= 0 AND (paid_amount <= approved_amount OR exception_documented))",
        ],
        "public_subsidies": [
            "CONSTRAINT ck_subsidy_dates CHECK (period_end >= period_start)",
            "CONSTRAINT ck_subsidy_amounts CHECK (approved_amount >= 0 AND paid_amount >= 0 AND paid_amount <= approved_amount)",
        ],
        "multi_year_commitments": [
            "CONSTRAINT ck_commitment_years CHECK (end_year >= start_year)",
            "CONSTRAINT ck_commitment_amount CHECK (total_committed_amount >= 0)",
        ],
    }
    for table, clauses in constraints.items():
        for clause in clauses:
            op.execute(f"ALTER TABLE {table} ADD {clause}")

    op.execute("""
    CREATE FUNCTION public_debt_guard() RETURNS trigger AS $$
    DECLARE evidence_source uuid; instrument record; disbursed numeric;
    BEGIN
      IF current_setting('app.actor_type', true) = 'ai' OR NEW.actor_type = 'ai' THEN
        RAISE EXCEPTION 'AI actors cannot write canonical public debt data';
      END IF;
      IF NEW.source_id IS NULL OR NEW.evidence_id IS NULL THEN
        RAISE EXCEPTION 'Canonical public debt data requires source and evidence';
      END IF;
      SELECT source_id INTO evidence_source FROM evidence WHERE id = NEW.evidence_id;
      IF evidence_source IS DISTINCT FROM NEW.source_id THEN
        RAISE EXCEPTION 'Source must match evidence source';
      END IF;
      RETURN NEW;
    END; $$ LANGUAGE plpgsql;
    """)
    canonical = (
        "creditors",
        "debt_instruments",
        "debt_service_schedules",
        "public_guarantees",
        "public_obligations",
        "financial_transfers",
        "public_subsidies",
        "multi_year_commitments",
    )
    for table in canonical:
        op.execute(f"""CREATE TRIGGER trg_{table}_guard BEFORE INSERT OR UPDATE ON {table}
                    FOR EACH ROW EXECUTE FUNCTION public_debt_guard()""")

    op.execute("""
    CREATE FUNCTION debt_compatibility_guard() RETURNS trigger AS $$
    DECLARE instrument record; cumulative numeric;
    BEGIN
      SELECT * INTO instrument FROM debt_instruments WHERE id = NEW.debt_instrument_id;
      IF NEW.debtor_institution_id <> instrument.debtor_institution_id THEN
        RAISE EXCEPTION 'Debt institution is incompatible with instrument';
      END IF;
      IF TG_TABLE_NAME = 'debt_payments' THEN
        IF NEW.creditor_id IS NOT NULL
           AND NEW.creditor_id IS DISTINCT FROM instrument.creditor_id THEN
          RAISE EXCEPTION 'Debt creditor is incompatible with instrument';
        END IF;
      END IF;
      IF TG_TABLE_NAME = 'debt_disbursements' THEN
        SELECT coalesce(sum(amount), 0) INTO cumulative FROM debt_disbursements
          WHERE debt_instrument_id = NEW.debt_instrument_id AND id <> NEW.id;
        IF cumulative + NEW.amount > coalesce(instrument.approved_amount, instrument.original_principal)
           AND NOT NEW.exception_documented THEN
          RAISE EXCEPTION 'Accumulated disbursements exceed approved amount';
        END IF;
      END IF;
      RETURN NEW;
    END; $$ LANGUAGE plpgsql;
    CREATE TRIGGER trg_disbursement_compatibility BEFORE INSERT OR UPDATE ON debt_disbursements
      FOR EACH ROW EXECUTE FUNCTION debt_compatibility_guard();
    CREATE TRIGGER trg_payment_compatibility BEFORE INSERT OR UPDATE ON debt_payments
      FOR EACH ROW EXECUTE FUNCTION debt_compatibility_guard();
    """)
    op.execute("""
    CREATE FUNCTION commitment_breakdown_guard() RETURNS trigger AS $$
    DECLARE total numeric;
    BEGIN
      SELECT coalesce(sum(value::numeric), 0) INTO total FROM jsonb_each_text(NEW.annual_breakdown);
      IF abs(total - NEW.total_committed_amount) > 0.01 THEN
        RAISE EXCEPTION 'Annual breakdown must equal total commitment';
      END IF;
      RETURN NEW;
    END; $$ LANGUAGE plpgsql;
    CREATE TRIGGER trg_commitment_breakdown BEFORE INSERT OR UPDATE ON multi_year_commitments
      FOR EACH ROW EXECUTE FUNCTION commitment_breakdown_guard();
    """)


def downgrade() -> None:
    op.execute("DROP FUNCTION IF EXISTS commitment_breakdown_guard() CASCADE")
    op.execute("DROP FUNCTION IF EXISTS debt_compatibility_guard() CASCADE")
    op.execute("DROP FUNCTION IF EXISTS public_debt_guard() CASCADE")
    for name in reversed(TABLES):
        op.drop_table(name)
