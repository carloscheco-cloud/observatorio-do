from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from alembic.config import Config
from sqlalchemy import create_engine, func, inspect, select, text
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.orm import Session

from alembic import command
from app.modules.digital_transparency.checks import MANIFEST_VERSION, rollback_checks
from app.modules.digital_transparency.loader import load
from app.modules.digital_transparency.models import (
    DigitalTransparencyLoadRecord,
    DocumentResource,
    ResourceCheck,
    ResourceCheckStatus,
    ResourceCheckType,
    SearchabilityCheck,
    SearchabilityMethod,
    SearchabilityResult,
    TransparencyAssessment,
)
from app.modules.digital_transparency.resource_checks import create_resource_check
from app.modules.digital_transparency.schemas import (
    ResourceCheckCreate,
    SearchabilityCheckCreate,
)
from app.modules.digital_transparency.searchability_checks import create_searchability_check
from app.modules.executive_authorities.loader import load_authorities
from app.modules.executive_dependencies.loader import load_dependencies
from app.modules.executive_inventory.loader import load_inventory
from tests.integration.test_postgresql_guards import BACKEND_DIR, migrate

pytestmark = pytest.mark.integration


def _config(postgres_url: str) -> Config:
    config = Config(BACKEND_DIR / "alembic.ini")
    config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    config.set_main_option("sqlalchemy.url", postgres_url)
    return config


def test_pe06a_migration_history_rollback_and_round_trip(postgres_url: str) -> None:
    migrate(postgres_url)
    engine = create_engine(postgres_url)
    now = datetime(2026, 8, 3, 12, tzinfo=UTC)
    with Session(engine) as db:
        load_inventory(db)
        load_dependencies(db)
        load_authorities(db)
        load(db)
        pe05_assessments = db.scalar(select(func.count()).select_from(TransparencyAssessment))
        assert pe05_assessments == 25
        assert db.scalar(select(func.count()).select_from(ResourceCheck)) == 0
        assert db.scalar(select(func.count()).select_from(SearchabilityCheck)) == 0
        resource = db.scalar(select(DocumentResource).limit(1))
        assert resource is not None
        first = create_resource_check(
            db,
            ResourceCheckCreate(
                resource_id=str(resource.id),
                checked_at=now,
                check_type=ResourceCheckType.HTTP_AVAILABILITY,
                status=ResourceCheckStatus.NOT_FOUND_PROVISIONAL,
                http_status=404,
                attempt_number=1,
                user_agent="OED-pytest-fixture/1.0",
                timeout_seconds=10,
                tool_name="pytest-fixture",
                tool_version="1",
                notes="Fixture técnico simulado; nunca es dato productivo.",
            ),
        )
        second = create_resource_check(
            db,
            ResourceCheckCreate(
                resource_id=str(resource.id),
                checked_at=now + timedelta(days=1),
                check_type=ResourceCheckType.HTTP_AVAILABILITY,
                status=ResourceCheckStatus.BROKEN_LINK_CONFIRMED,
                http_status=404,
                attempt_number=2,
                user_agent="OED-pytest-fixture/1.0",
                timeout_seconds=10,
                tool_name="pytest-fixture",
                tool_version="1",
                notes="Segunda fixture técnica simulada; nunca es dato productivo.",
            ),
        )
        searchability = create_searchability_check(
            db,
            SearchabilityCheckCreate(
                resource_id=str(resource.id),
                checked_at=now,
                method=SearchabilityMethod.PDF_TEXT_EXTRACTION,
                result=SearchabilityResult.INCONCLUSIVE,
                tool_name="pytest-fixture",
                tool_version="1",
                notes="Fixture técnico simulado sin OCR; nunca es dato productivo.",
            ),
        )
        for kind, identifier in (
            ("resource_check", first.id),
            ("resource_check", second.id),
            ("searchability_check", searchability.id),
        ):
            db.add(
                DigitalTransparencyLoadRecord(
                    manifest_version=MANIFEST_VERSION,
                    record_type=kind,
                    record_id=identifier,
                )
            )
        db.commit()
        assert db.scalar(select(func.count()).select_from(ResourceCheck)) == 2
        assert db.scalar(select(func.count()).select_from(SearchabilityCheck)) == 1
        with pytest.raises(IntegrityError):
            create_resource_check(
                db,
                ResourceCheckCreate(
                    resource_id=str(resource.id),
                    checked_at=now,
                    check_type=ResourceCheckType.HTTP_AVAILABILITY,
                    status=ResourceCheckStatus.NOT_FOUND_PROVISIONAL,
                    http_status=404,
                    attempt_number=1,
                    user_agent="OED-pytest-fixture/1.0",
                    timeout_seconds=10,
                    tool_name="pytest-fixture",
                    tool_version="1",
                ),
            )
        db.rollback()
        with pytest.raises((ValueError, DBAPIError), match="immutable"):
            first.notes = "forbidden mutation"
            db.commit()
        db.rollback()
        preview = rollback_checks(db, dry_run=True)
        assert preview.removed == 6
        assert db.scalar(select(func.count()).select_from(ResourceCheck)) == 2
        rollback_checks(db)
        assert db.scalar(select(func.count()).select_from(ResourceCheck)) == 0
        assert db.scalar(select(func.count()).select_from(SearchabilityCheck)) == 0
        assert db.scalar(select(func.count()).select_from(TransparencyAssessment)) == 25

    config = _config(postgres_url)
    command.downgrade(config, "0015")
    assert "transparency_resource_checks" not in inspect(engine).get_table_names()
    command.upgrade(config, "0016")
    assert "transparency_resource_checks" in inspect(engine).get_table_names()
    with engine.connect() as connection:
        assert connection.scalar(text("SELECT version_num FROM alembic_version")) == "0016"
        assert connection.scalar(text("SELECT count(*) FROM transparency_resource_checks")) == 0
        assert (
            connection.scalar(text("SELECT count(*) FROM transparency_searchability_checks")) == 0
        )
        assert connection.scalar(text("SELECT count(*) FROM transparency_assessments")) == 25
