from __future__ import annotations

import hashlib
import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.ingestion.models import (
    ColumnMapping,
    DataQualityIssue,
    ImportSchema,
    IngestionRun,
    IngestionSchedule,
    QuarantineRecord,
    RawArtifact,
    SourceCatalog,
    SourceQualityMetric,
    StagingBatch,
    StagingRecord,
)


def seed_ingestion(db: Session, source_id: uuid.UUID) -> None:
    for code, name, method, source_type in (
        ("mock-http", "Portal HTTP ficticio", "HTTP_GET", "downloadable_file"),
        ("mock-api", "API oficial ficticia", "API", "API"),
        ("mock-manual", "Carga manual controlada", "manual", "manual_upload"),
    ):
        catalog = db.scalar(select(SourceCatalog).where(SourceCatalog.stable_code == code))
        if catalog is None:
            catalog = SourceCatalog(
                source_id=source_id,
                stable_code=code,
                official_name=name,
                source_type=source_type,
                base_url=None,
                jurisdiction="DO",
                data_domains=["institutions"],
                access_method=method,
                authentication_type="none",
                update_frequency="manual",
                expected_formats=["CSV"],
                active=True,
                priority=100,
                reliability_level="test",
                configuration={"connector": "mock"},
                metadata_={"fictitious": True},
            )
            db.add(catalog)
            db.flush()
    catalog = db.scalar(select(SourceCatalog).where(SourceCatalog.stable_code == "mock-http"))
    assert catalog is not None
    schema = db.scalar(
        select(ImportSchema).where(
            ImportSchema.stable_code == "mock-institutions", ImportSchema.version == 1
        )
    )
    if schema is None:
        schema = ImportSchema(
            stable_code="mock-institutions",
            name="Instituciones ficticias",
            domain="institutions",
            version=1,
            source_catalog_id=catalog.id,
            target_entity_type="institution",
            expected_columns=["code", "name"],
            required_columns=["code", "name"],
            optional_columns=[],
            column_aliases={},
            data_types={"code": "string", "name": "string"},
            transformations={"name": ["trim", "unicode"]},
            validations={},
            deduplication_config={"fields": ["code"]},
            canonical_service="institutions.service",
            status="active",
            valid_from=date(2026, 1, 1),
            approved_by_actor_id=uuid.UUID("00000000-0000-0000-0000-000000000011"),
            metadata_={"fictitious": True},
        )
        db.add(schema)
        db.flush()
        db.add(
            ColumnMapping(
                import_schema_id=schema.id,
                source_column="nombre",
                normalized_column="name",
                target_field="name",
                transformation_type="trim",
                transformation_config={},
                confidence_level="high",
                mapping_origin="configured",
                approved=True,
                metadata_={},
            )
        )
    run = db.scalar(select(IngestionRun).where(IngestionRun.run_code == "seed-run-completed"))
    if run is None:
        checksum = hashlib.sha256(b"code,name\nMOCK,Institucion ficticia\n").hexdigest()
        run = IngestionRun(
            run_code="seed-run-completed",
            source_catalog_id=catalog.id,
            connector_type="MockConnector",
            trigger_type="manual",
            status="completed",
            requested_by_actor_type="human",
            attempt_number=1,
            configuration_snapshot={"mock": True},
            checksum=checksum,
            engine_version="11.0",
            completed_at=datetime.now(UTC),
            downloaded_files=1,
            parsed_records=2,
            valid_records=1,
            invalid_records=1,
            warnings_count=1,
            metadata_={"fictitious": True},
        )
        db.add(run)
        db.flush()
        artifact = RawArtifact(
            ingestion_run_id=run.id,
            source_catalog_id=catalog.id,
            artifact_type="CSV",
            original_filename="fictitious.csv",
            storage_key=f"seed/{checksum}.csv",
            mime_type_detected="text/csv",
            mime_type_reported="text/csv",
            size_bytes=39,
            checksum_sha256=checksum,
            retention_policy="test",
            metadata_={"fictitious": True},
        )
        db.add(artifact)
        batch = StagingBatch(
            ingestion_run_id=run.id,
            import_schema_id=schema.id,
            domain="institutions",
            entity_type="institution",
            status="validated",
            total_records=2,
            valid_records=1,
            invalid_records=1,
        )
        db.add(batch)
        db.flush()
        invalid = StagingRecord(
            staging_batch_id=batch.id,
            row_number=3,
            raw_data={"code": "", "name": ""},
            validation_status="invalid",
            validation_errors=[{"code": "required_missing"}],
            validation_warnings=[],
            canonical_action="reject",
            metadata_={},
        )
        db.add(invalid)
        db.flush()
        db.add(
            DataQualityIssue(
                ingestion_run_id=run.id,
                staging_record_id=invalid.id,
                issue_code="required_missing",
                domain="institutions",
                severity="error",
                issue_type="schema",
                field_name="code",
                message="Fictitious required field is absent",
                status="open",
                metadata_={},
            )
        )
        db.add(
            QuarantineRecord(
                ingestion_run_id=run.id,
                raw_artifact_id=artifact.id,
                quarantine_reason="suspicious_content",
                severity="warning",
                status="reviewed",
                resolution="Fictitious seed only",
                metadata_={},
            )
        )
    if not db.scalar(
        select(IngestionSchedule.id).where(IngestionSchedule.source_catalog_id == catalog.id)
    ):
        db.add(
            IngestionSchedule(
                source_catalog_id=catalog.id,
                schedule_type="interval",
                interval_minutes=1440,
                timezone="America/Santo_Domingo",
                enabled=False,
                retry_policy={"max_attempts": 3},
                overlap_policy="skip",
                maximum_runtime_seconds=3600,
                metadata_={"fictitious": True},
            )
        )
    if not db.scalar(
        select(SourceQualityMetric.id).where(SourceQualityMetric.source_catalog_id == catalog.id)
    ):
        db.add(
            SourceQualityMetric(
                source_catalog_id=catalog.id,
                calculation_date=date(2026, 1, 1),
                availability_score=Decimal(100),
                timeliness_score=Decimal(100),
                completeness_score=Decimal(50),
                consistency_score=Decimal(100),
                parseability_score=Decimal(100),
                traceability_score=Decimal(100),
                historical_stability_score=Decimal(100),
                total_score=Decimal("92.86"),
                observations={"fictitious": True},
                metadata_={},
            )
        )
    db.flush()
