# ruff: noqa: E501
"""Block 11: controlled ingestion, ETL, quality, and lineage.

Revision ID: 0011
Revises: 0010
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0011"
down_revision: str | None = "0010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TABLES = (
    "source_catalog",
    "ingestion_runs",
    "raw_artifacts",
    "source_discoveries",
    "import_schemas",
    "column_mappings",
    "staging_batches",
    "staging_records",
    "data_quality_issues",
    "entity_match_candidates",
    "data_lineage_links",
    "ingestion_versions",
    "source_quality_metrics",
    "ingestion_schedules",
    "ingestion_jobs",
    "quarantine_records",
)


def upgrade() -> None:
    from app.db.base import Base
    from app.modules import models  # noqa: F401

    bind = op.get_bind()
    for name in TABLES:
        Base.metadata.tables[name].create(bind=bind)

    checks = {
        "source_catalog": [
            "CONSTRAINT ck_source_type CHECK (source_type IN ('official_portal','transparency_portal','open_data_portal','institutional_website','API','downloadable_file','RSS','database_export','manual_upload','other'))",
            "CONSTRAINT ck_source_method CHECK (access_method IN ('HTTP_GET','HTTP_POST','API','SFTP','manual','browser_required','other'))",
            "CONSTRAINT ck_source_auth CHECK (authentication_type IN ('none','API key','bearer','basic','OAuth','session','manual','other'))",
            "CONSTRAINT ck_source_configuration_no_secrets CHECK (NOT (configuration ?| ARRAY['password','token','secret','api_key','authorization','cookie']))",
        ],
        "ingestion_runs": [
            "CONSTRAINT ck_ingestion_status CHECK (status IN ('queued','discovering','downloading','downloaded','parsing','validating','normalizing','staging','canonicalizing','completed','completed_with_warnings','failed','cancelled','skipped_unchanged','quarantined'))",
            "CONSTRAINT ck_ingestion_trigger CHECK (trigger_type IN ('manual','scheduled','retry','backfill','source_change','file_upload','API_event','other'))",
            "CONSTRAINT ck_ingestion_actor CHECK (requested_by_actor_type <> 'ai')",
            "CONSTRAINT ck_ingestion_counts CHECK (attempt_number > 0 AND downloaded_files >= 0 AND discovered_records >= 0 AND parsed_records >= 0 AND valid_records >= 0 AND invalid_records >= 0 AND canonical_records_created >= 0 AND canonical_records_updated >= 0 AND canonical_records_unchanged >= 0 AND evidence_records_created >= 0 AND warnings_count >= 0 AND errors_count >= 0)",
            "CONSTRAINT ck_ingestion_dates CHECK (completed_at IS NULL OR completed_at >= started_at)",
        ],
        "raw_artifacts": [
            "CONSTRAINT ck_artifact_checksum CHECK (checksum_sha256 ~ '^[0-9a-f]{64}$')",
            "CONSTRAINT ck_artifact_size CHECK (size_bytes >= 0)",
        ],
        "source_discoveries": [
            "CONSTRAINT ck_discovery_status CHECK (discovery_status IN ('new','changed','unchanged','processed','rejected','unavailable','ignored','under_review'))",
        ],
        "import_schemas": [
            "CONSTRAINT uq_import_schema_version UNIQUE (stable_code, version)",
            "CONSTRAINT ck_import_schema_version CHECK (version > 0)",
            "CONSTRAINT ck_import_schema_status CHECK (status IN ('draft','under_review','approved','active','deprecated','retired'))",
            "CONSTRAINT ck_import_schema_approval CHECK (status NOT IN ('approved','active') OR approved_by_actor_id IS NOT NULL)",
            "CONSTRAINT ck_import_schema_dates CHECK (valid_to IS NULL OR valid_to >= valid_from)",
        ],
        "column_mappings": [
            "CONSTRAINT ck_ai_mapping_approval CHECK (mapping_origin <> 'AI proposed' OR approved = false)",
        ],
        "staging_batches": [
            "CONSTRAINT ck_staging_batch_counts CHECK (total_records >= 0 AND valid_records >= 0 AND invalid_records >= 0 AND duplicate_records >= 0 AND review_records >= 0)",
        ],
        "staging_records": [
            "CONSTRAINT ck_staging_validation CHECK (validation_status IN ('pending','valid','invalid','warning','duplicate','needs_review','rejected','canonicalized'))",
            "CONSTRAINT ck_staging_action CHECK (canonical_action IN ('create','update','unchanged','skip','review','reject'))",
            "CONSTRAINT ck_canonical_staging_valid CHECK (validation_status <> 'canonicalized' OR canonical_action IN ('create','update','unchanged'))",
        ],
        "data_quality_issues": [
            "CONSTRAINT ck_quality_severity CHECK (severity IN ('info','warning','error','critical','quarantine'))",
        ],
        "data_lineage_links": [
            "CONSTRAINT ck_lineage_entity CHECK (length(trim(canonical_entity_type)) > 0)",
            "CONSTRAINT ck_lineage_type CHECK (lineage_type IN ('created_from','updated_from','verified_by','compared_with','derived_from','normalized_from','other'))",
        ],
        "ingestion_schedules": [
            "CONSTRAINT ck_schedule_definition CHECK ((cron_expression IS NULL) <> (interval_minutes IS NULL))",
            "CONSTRAINT ck_schedule_interval CHECK (interval_minutes IS NULL OR interval_minutes > 0)",
            "CONSTRAINT ck_schedule_runtime CHECK (maximum_runtime_seconds > 0)",
            "CONSTRAINT ck_schedule_overlap CHECK (overlap_policy IN ('skip','queue','cancel_previous','allow'))",
        ],
        "ingestion_jobs": [
            "CONSTRAINT ck_job_attempts CHECK (attempts >= 0 AND max_attempts > 0 AND attempts <= max_attempts)",
        ],
        "quarantine_records": [
            "CONSTRAINT ck_quarantine_reason CHECK (quarantine_reason IN ('malicious_file','oversized_file','zip_bomb_risk','unsupported_format','invalid_schema','sensitive_data_exposure','corrupted_file','suspicious_content','repeated_failure','other'))",
        ],
    }
    for table, clauses in checks.items():
        for clause in clauses:
            op.execute(f"ALTER TABLE {table} ADD {clause}")

    op.execute("""
    CREATE FUNCTION ingestion_history_guard() RETURNS trigger AS $$
    BEGIN
      IF TG_TABLE_NAME = 'raw_artifacts' THEN
        RAISE EXCEPTION 'Raw artifacts are immutable';
      END IF;
      IF OLD.status IN ('completed','completed_with_warnings','failed','cancelled','skipped_unchanged','quarantined') THEN
        RAISE EXCEPTION 'Closed ingestion runs are immutable';
      END IF;
      RETURN NEW;
    END; $$ LANGUAGE plpgsql;
    CREATE TRIGGER trg_raw_artifacts_immutable BEFORE UPDATE OR DELETE ON raw_artifacts
      FOR EACH ROW EXECUTE FUNCTION ingestion_history_guard();
    CREATE TRIGGER trg_closed_runs_immutable BEFORE UPDATE OR DELETE ON ingestion_runs
      FOR EACH ROW EXECUTE FUNCTION ingestion_history_guard();
    """)
    op.execute("""
    CREATE FUNCTION used_import_schema_guard() RETURNS trigger AS $$
    BEGIN
      IF EXISTS (SELECT 1 FROM staging_batches WHERE import_schema_id = OLD.id)
         AND (NEW.expected_columns, NEW.required_columns, NEW.column_aliases, NEW.data_types,
              NEW.transformations, NEW.validations, NEW.deduplication_config, NEW.canonical_service)
         IS DISTINCT FROM
             (OLD.expected_columns, OLD.required_columns, OLD.column_aliases, OLD.data_types,
              OLD.transformations, OLD.validations, OLD.deduplication_config, OLD.canonical_service) THEN
        RAISE EXCEPTION 'Used import schemas must be versioned';
      END IF;
      RETURN NEW;
    END; $$ LANGUAGE plpgsql;
    CREATE TRIGGER trg_used_import_schema_immutable BEFORE UPDATE ON import_schemas
      FOR EACH ROW EXECUTE FUNCTION used_import_schema_guard();
    """)
    op.execute("""
    CREATE UNIQUE INDEX uq_artifact_source_checksum
      ON raw_artifacts(source_catalog_id, checksum_sha256);
    CREATE UNIQUE INDEX uq_discovery_source_fingerprint
      ON source_discoveries(source_catalog_id, fingerprint);
    CREATE INDEX ix_jobs_claim
      ON ingestion_jobs(priority, scheduled_at) WHERE status IN ('queued','retry');
    CREATE INDEX ix_source_freshness
      ON source_catalog(active, next_expected_update_at, last_success_at);
    CREATE INDEX ix_lineage_entity
      ON data_lineage_links(canonical_entity_type, canonical_entity_id);
    CREATE INDEX ix_staging_dedup
      ON staging_records(staging_batch_id, deduplication_key);
    """)


def downgrade() -> None:
    op.execute("DROP FUNCTION IF EXISTS used_import_schema_guard() CASCADE")
    op.execute("DROP FUNCTION IF EXISTS ingestion_history_guard() CASCADE")
    for name in reversed(TABLES):
        op.drop_table(name)
