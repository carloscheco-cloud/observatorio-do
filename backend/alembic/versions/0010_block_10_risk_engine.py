# ruff: noqa: E501
"""Block 10: cross-domain observable signals and human review.

Revision ID: 0010
Revises: 0009
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0010"
down_revision: str | None = "0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TABLES = (
    "risk_domains",
    "risk_categories",
    "risk_types",
    "risk_indicators",
    "risk_rules",
    "risk_evaluation_runs",
    "risk_findings",
    "finding_evidence_links",
    "finding_entity_links",
    "finding_groups",
    "finding_duplicates",
    "finding_reviews",
    "risk_suppressions",
    "risk_thresholds",
    "risk_scores",
    "audit_events",
)


def upgrade() -> None:
    from app.db.base import Base
    from app.modules import models  # noqa: F401

    bind = op.get_bind()
    for name in TABLES:
        Base.metadata.tables[name].create(bind=bind)

    checks = {
        "risk_domains": [
            "CONSTRAINT ck_risk_domain_dates CHECK (valid_to IS NULL OR valid_to >= valid_from)"
        ],
        "risk_categories": [
            "CONSTRAINT ck_risk_category_dates CHECK (valid_to IS NULL OR valid_to >= valid_from)"
        ],
        "risk_types": [
            "CONSTRAINT ck_risk_type_dates CHECK (valid_to IS NULL OR valid_to >= valid_from)",
            "CONSTRAINT ck_risk_type_severity CHECK (default_severity IN ('informational','review_required','unusual','high_priority','critical_data_quality'))",
        ],
        "risk_indicators": [
            "CONSTRAINT ck_risk_indicator_dates CHECK (valid_to IS NULL OR valid_to >= valid_from)",
            "CONSTRAINT ck_risk_indicator_severity CHECK (default_severity IN ('informational','review_required','unusual','high_priority','critical_data_quality'))",
        ],
        "risk_rules": [
            "CONSTRAINT uq_risk_rule_version UNIQUE (stable_code, version)",
            "CONSTRAINT ck_risk_rule_version CHECK (version > 0)",
            "CONSTRAINT ck_risk_rule_dates CHECK (valid_to IS NULL OR valid_to >= valid_from)",
            "CONSTRAINT ck_risk_rule_type CHECK (rule_type IN ('deterministic','threshold','comparative','historical','statistical','cross_domain','data_quality','scheduled','manually_triggered','ai_assisted','other'))",
            "CONSTRAINT ck_ai_rule_activation CHECK (created_by_actor_type <> 'ai' OR enabled = false)",
        ],
        "risk_evaluation_runs": [
            "CONSTRAINT ck_risk_run_status CHECK (status IN ('queued','running','completed','completed_with_errors','failed','cancelled'))",
            "CONSTRAINT ck_risk_run_trigger CHECK (trigger_type IN ('scheduled','event_driven','manual','import_completed','period_closed','data_updated','backfill','other'))",
            "CONSTRAINT ck_risk_run_dates CHECK (completed_at IS NULL OR completed_at >= started_at)",
            "CONSTRAINT ck_risk_run_counts CHECK (rules_requested >= 0 AND rules_executed >= 0 AND records_evaluated >= 0 AND findings_created >= 0 AND findings_updated >= 0 AND findings_suppressed >= 0 AND errors_count >= 0)",
        ],
        "risk_findings": [
            "CONSTRAINT ck_risk_finding_dates CHECK (period_end IS NULL OR period_start IS NULL OR period_end >= period_start)",
            "CONSTRAINT ck_risk_finding_detection CHECK (last_detected_at >= first_detected_at)",
            "CONSTRAINT ck_risk_finding_counts CHECK (occurrence_count > 0 AND evidence_count >= 0)",
            "CONSTRAINT ck_risk_finding_severity CHECK (severity IN ('informational','review_required','unusual','high_priority','critical_data_quality'))",
            "CONSTRAINT ck_risk_finding_confidence CHECK (confidence_level IN ('low','medium','high','deterministic'))",
            "CONSTRAINT ck_risk_finding_status CHECK (status IN ('detected','pending_review','confirmed_signal','dismissed','resolved','monitoring','suppressed','duplicate','expired','reopened'))",
            "CONSTRAINT ck_risk_finding_visibility CHECK (visibility IN ('internal','restricted','public','embargoed'))",
            "CONSTRAINT ck_public_explanation CHECK (visibility <> 'public' OR length(trim(public_explanation)) > 0)",
        ],
        "finding_evidence_links": [
            "CONSTRAINT uq_finding_evidence UNIQUE (finding_id, evidence_id, relationship_type)",
            "CONSTRAINT ck_relevance_score CHECK (relevance_score IS NULL OR relevance_score BETWEEN 0 AND 1)",
            "CONSTRAINT ck_evidence_relationship CHECK (relationship_type IN ('primary','supporting','comparison','contradictory','historical','contextual','other'))",
        ],
        "finding_entity_links": [
            "CONSTRAINT uq_finding_entity_role UNIQUE (finding_id, entity_type, entity_id, relationship_role)",
            "CONSTRAINT ck_entity_role CHECK (relationship_role IN ('subject','related','origin','destination','beneficiary','comparison','historical_reference','reviewer_context','other'))",
        ],
        "finding_duplicates": [
            "CONSTRAINT ck_duplicate_self CHECK (finding_id <> canonical_finding_id)"
        ],
        "finding_reviews": [
            "CONSTRAINT ck_review_action CHECK (review_action IN ('confirm','dismiss','request_more_evidence','change_severity','merge_duplicate','mark_resolved','reopen','suppress','publish','restrict','other'))",
            "CONSTRAINT ck_review_actor CHECK (reviewer_actor_id IS NOT NULL)",
        ],
        "risk_suppressions": [
            "CONSTRAINT ck_suppression_reason CHECK (length(trim(reason)) > 0)",
            "CONSTRAINT ck_suppression_dates CHECK (valid_to IS NULL OR valid_to >= valid_from)",
        ],
        "risk_thresholds": [
            "CONSTRAINT uq_risk_threshold_version UNIQUE (risk_rule_id, scope_type, scope_id, threshold_key, valid_from)",
            "CONSTRAINT ck_threshold_dates CHECK (valid_to IS NULL OR valid_to >= valid_from)",
        ],
        "risk_scores": [
            "CONSTRAINT uq_risk_score_version UNIQUE (entity_type, entity_id, period_start, period_end, model_or_formula_version)",
            "CONSTRAINT ck_risk_score_range CHECK (total_score BETWEEN 0 AND 100 AND data_quality_penalty >= 0)",
            "CONSTRAINT ck_risk_score_dates CHECK (period_end >= period_start)",
            "CONSTRAINT ck_risk_score_band CHECK (score_band IN ('insufficient_data','low','moderate','elevated','high_review_priority'))",
        ],
    }
    for table, clauses in checks.items():
        for clause in clauses:
            op.execute(f"ALTER TABLE {table} ADD {clause}")

    op.execute("""
    CREATE FUNCTION risk_finding_integrity_guard() RETURNS trigger AS $$
    BEGIN
      IF current_setting('app.actor_type', true) = 'ai'
         AND NEW.status NOT IN ('detected','pending_review') THEN
        RAISE EXCEPTION 'AI actors can only propose unconfirmed findings';
      END IF;
      IF NEW.status = 'confirmed_signal' AND NOT EXISTS (
        SELECT 1 FROM finding_evidence_links WHERE finding_id = NEW.id
      ) THEN
        RAISE EXCEPTION 'Confirmed signal requires linked evidence';
      END IF;
      IF NEW.visibility = 'public' AND (
        NEW.reviewed_by_actor_id IS NULL OR NEW.reviewed_at IS NULL
        OR NOT EXISTS (SELECT 1 FROM finding_evidence_links WHERE finding_id = NEW.id)
      ) THEN
        RAISE EXCEPTION 'Public signal requires human review and evidence';
      END IF;
      RETURN NEW;
    END; $$ LANGUAGE plpgsql;
    CREATE CONSTRAINT TRIGGER trg_risk_finding_integrity
      AFTER INSERT OR UPDATE ON risk_findings DEFERRABLE INITIALLY DEFERRED
      FOR EACH ROW EXECUTE FUNCTION risk_finding_integrity_guard();
    """)
    op.execute("""
    CREATE FUNCTION immutable_analytic_history() RETURNS trigger AS $$
    BEGIN
      RAISE EXCEPTION 'Analytic history is immutable';
    END; $$ LANGUAGE plpgsql;
    CREATE TRIGGER trg_audit_events_immutable BEFORE UPDATE OR DELETE ON audit_events
      FOR EACH ROW EXECUTE FUNCTION immutable_analytic_history();
    CREATE TRIGGER trg_finding_reviews_immutable BEFORE UPDATE OR DELETE ON finding_reviews
      FOR EACH ROW EXECUTE FUNCTION immutable_analytic_history();
    """)
    op.execute("""
    CREATE FUNCTION used_risk_rule_immutable() RETURNS trigger AS $$
    BEGIN
      IF EXISTS (SELECT 1 FROM risk_findings WHERE risk_rule_id = OLD.id) AND
         (NEW.stable_code, NEW.rule_type, NEW.version, NEW.threshold_config,
          NEW.evaluation_window, NEW.required_fields, NEW.supported_entity_types)
         IS DISTINCT FROM
         (OLD.stable_code, OLD.rule_type, OLD.version, OLD.threshold_config,
          OLD.evaluation_window, OLD.required_fields, OLD.supported_entity_types) THEN
        RAISE EXCEPTION 'A rule used by an evaluation must be versioned';
      END IF;
      RETURN NEW;
    END; $$ LANGUAGE plpgsql;
    CREATE TRIGGER trg_used_risk_rule_immutable BEFORE UPDATE ON risk_rules
      FOR EACH ROW EXECUTE FUNCTION used_risk_rule_immutable();
    """)
    op.execute("""
    CREATE INDEX ix_risk_findings_metrics ON risk_findings(domain, severity, status, period_start);
    CREATE INDEX ix_risk_findings_institution_history ON risk_findings(institution_id, last_detected_at DESC);
    CREATE INDEX ix_risk_findings_review_queue ON risk_findings(requires_human_review, status, severity);
    CREATE INDEX ix_risk_findings_recurrence ON risk_findings(occurrence_count DESC, last_detected_at DESC);
    CREATE INDEX ix_audit_events_history ON audit_events(entity_type, entity_id, occurred_at DESC);
    CREATE INDEX ix_risk_scores_period ON risk_scores(entity_type, entity_id, period_start, period_end);
    """)


def downgrade() -> None:
    op.execute("DROP FUNCTION IF EXISTS used_risk_rule_immutable() CASCADE")
    op.execute("DROP FUNCTION IF EXISTS immutable_analytic_history() CASCADE")
    op.execute("DROP FUNCTION IF EXISTS risk_finding_integrity_guard() CASCADE")
    for name in reversed(TABLES):
        op.drop_table(name)
