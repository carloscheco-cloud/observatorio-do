from __future__ import annotations

import hashlib
import uuid
from datetime import UTC, datetime

import pytest
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, text
from sqlalchemy.exc import DBAPIError

from tests.integration.test_postgresql_guards import BACKEND_DIR, migrate

pytestmark = pytest.mark.integration


def _source(connection: object) -> tuple[uuid.UUID, uuid.UUID]:
    suffix = uuid.uuid4().hex
    source_id = connection.scalar(  # type: ignore[attr-defined]
        text(
            "INSERT INTO sources (id,name,url,publisher,is_official) "
            "VALUES (gen_random_uuid(),'Mock',:url,'Test',true) "
            "RETURNING id"
        ),
        {"url": f"https://example.test/{suffix}"},
    )
    catalog_id = connection.scalar(  # type: ignore[attr-defined]
        text(
            "INSERT INTO source_catalog "
            "(id,source_id,stable_code,official_name,source_type,jurisdiction,data_domains,"
            "access_method,authentication_type,update_frequency,expected_formats,active,priority,"
            "reliability_level,configuration,metadata) VALUES "
            "(gen_random_uuid(),:source,:code,'Mock','manual_upload','DO','[]','manual','none',"
            "'manual','[\"CSV\"]',true,100,'test','{}','{}') RETURNING id"
        ),
        {"source": source_id, "code": f"pg-mock-{suffix}"},
    )
    return source_id, catalog_id


def test_block_11_schema_and_single_head(postgres_url: str) -> None:
    migrate(postgres_url)
    config = Config(BACKEND_DIR / "alembic.ini")
    config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    script = ScriptDirectory.from_config(config)
    heads = script.get_heads()

    assert len(heads) == 1
    executive_revision = script.get_revision("0013")
    assert executive_revision is not None

    engine = create_engine(postgres_url)
    with engine.connect() as connection:
        current = connection.scalar(text("SELECT version_num FROM alembic_version"))
        assert current == heads[0]
        assert executive_revision.revision == "0013"
        assert current == "0018"
        tables = connection.execute(
            text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema='public' AND table_name IN "
                "('source_catalog','ingestion_runs','raw_artifacts','staging_records',"
                "'data_lineage_links','ingestion_jobs')"
            )
        ).scalars()
        assert len(set(tables)) == 6


def test_raw_artifact_and_closed_run_are_immutable(postgres_url: str) -> None:
    migrate(postgres_url)
    engine = create_engine(postgres_url)
    with engine.begin() as connection:
        _, catalog_id = _source(connection)
        run_code = f"pg-run-{uuid.uuid4().hex}"
        run_id = connection.scalar(
            text(
                "INSERT INTO ingestion_runs "
                "(id,run_code,source_catalog_id,connector_type,trigger_type,status,"
                "requested_by_actor_type,attempt_number,configuration_snapshot,engine_version,"
                "completed_at,metadata,downloaded_files,discovered_records,parsed_records,"
                "valid_records,invalid_records,canonical_records_created,"
                "canonical_records_updated,canonical_records_unchanged,"
                "evidence_records_created,warnings_count,errors_count,error_summary) VALUES "
                "(gen_random_uuid(),:code,:source,'Mock','manual','completed','human',1,'{}',"
                "'11.0',now(),'{}',0,0,0,0,0,0,0,0,0,0,0,'{}') RETURNING id"
            ),
            {"source": catalog_id, "code": run_code},
        )
        checksum = hashlib.sha256(b"controlled").hexdigest()
        artifact_id = connection.scalar(
            text(
                "INSERT INTO raw_artifacts "
                "(id,ingestion_run_id,source_catalog_id,artifact_type,storage_key,"
                "mime_type_detected,size_bytes,checksum_sha256,retention_policy,metadata,"
                "downloaded_at,is_encrypted,is_quarantined,created_at) VALUES "
                "(gen_random_uuid(),:run,:source,'file','test/key','text/plain',10,:checksum,"
                "'test','{}',now(),false,false,now()) RETURNING id"
            ),
            {"run": run_id, "source": catalog_id, "checksum": checksum},
        )
    with engine.connect() as connection:
        transaction = connection.begin()
        with pytest.raises(DBAPIError, match="immutable"):
            connection.execute(
                text("UPDATE raw_artifacts SET storage_key='changed' WHERE id=:id"),
                {"id": artifact_id},
            )
        transaction.rollback()
    with engine.connect() as connection:
        transaction = connection.begin()
        with pytest.raises(DBAPIError, match="Closed"):
            connection.execute(
                text("UPDATE ingestion_runs SET errors_count=1 WHERE id=:id"), {"id": run_id}
            )
        transaction.rollback()


def test_job_claim_uses_skip_locked_and_ai_run_is_blocked(postgres_url: str) -> None:
    migrate(postgres_url)
    engine = create_engine(postgres_url)
    with engine.begin() as connection:
        _, catalog_id = _source(connection)
        job_id = connection.scalar(
            text(
                "INSERT INTO ingestion_jobs "
                "(id,source_catalog_id,job_type,priority,status,scheduled_at,attempts,max_attempts,"
                "payload) VALUES (gen_random_uuid(),:source,'ingest',1,'queued',now(),0,3,'{}') "
                "RETURNING id"
            ),
            {"source": catalog_id},
        )
    first = engine.connect()
    second = engine.connect()
    first_tx, second_tx = first.begin(), second.begin()
    try:
        one = first.scalar(
            text(
                "SELECT id FROM ingestion_jobs WHERE id=:id AND status='queued' "
                "FOR UPDATE SKIP LOCKED LIMIT 1"
            ),
            {"id": job_id},
        )
        two = second.scalar(
            text(
                "SELECT id FROM ingestion_jobs WHERE id=:id AND status='queued' "
                "FOR UPDATE SKIP LOCKED LIMIT 1"
            ),
            {"id": job_id},
        )
        assert one is not None and two is None
    finally:
        first_tx.rollback()
        second_tx.rollback()
        first.close()
        second.close()
    with engine.connect() as connection:
        transaction = connection.begin()
        with pytest.raises(DBAPIError):
            connection.execute(
                text(
                    "INSERT INTO ingestion_runs "
                    "(id,run_code,source_catalog_id,connector_type,trigger_type,status,"
                    "requested_by_actor_type,attempt_number,configuration_snapshot,engine_version,"
                    "metadata) VALUES "
                    "(gen_random_uuid(),:code,:source,'Mock','manual','queued','ai',"
                    "1,'{}','11.0','{}')"
                ),
                {"code": f"ai-{datetime.now(UTC).timestamp()}", "source": catalog_id},
            )
        transaction.rollback()
