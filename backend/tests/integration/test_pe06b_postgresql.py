import pytest
from alembic.config import Config
from sqlalchemy import create_engine, func, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from alembic import command
from app.modules.digital_transparency.loader import load as load_pe05
from app.modules.digital_transparency.models import (
    ResourceCheck,
    SearchabilityCheck,
    TransparencyAssessment,
)
from app.modules.digital_transparency.pe06b import load, recalculate, rollback
from app.modules.executive_authorities.loader import load_authorities
from app.modules.executive_inventory.loader import load_inventory
from tests.integration.test_postgresql_guards import BACKEND_DIR, migrate

pytestmark = pytest.mark.integration


def test_pe06b_postgresql_round_trip_preserves_pe05_and_pe06a(postgres_url: str) -> None:
    migrate(postgres_url)
    engine = create_engine(postgres_url)
    with Session(engine) as db:
        load_inventory(db)
        load_authorities(db)
        load_pe05(db)
        assert load(db, dry_run=True).created > 0
        first = load(db)
        second = load(db)
        assert first.created > 0 and second.unchanged > 0
        assert db.scalar(select(func.count()).select_from(ResourceCheck)) == 16
        assert db.scalar(select(func.count()).select_from(SearchabilityCheck)) == 15
        assert db.scalar(select(func.count()).select_from(TransparencyAssessment)) == 30
        assert recalculate(db).unchanged == 5
        assert rollback(db, dry_run=True).removed > 0
        rollback(db)
        assert db.scalar(select(func.count()).select_from(TransparencyAssessment)) == 25
        assert db.scalar(select(func.count()).select_from(ResourceCheck)) == 0
        assert db.scalar(select(func.count()).select_from(SearchabilityCheck)) == 0

        load(db)
        historical_assessments = db.scalar(text("SELECT count(*) FROM transparency_assessments"))
        historical_observations = db.scalar(text("SELECT count(*) FROM transparency_observations"))

        config = Config(BACKEND_DIR / "alembic.ini")
        config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
        config.set_main_option("sqlalchemy.url", postgres_url)
        command.downgrade(config, "0016")
        with engine.connect() as historical:
            assert not historical.scalar(
                text("SELECT to_regclass('transparency_methodologies') IS NOT NULL")
            )
            columns = set(
                historical.scalars(
                    text(
                        "SELECT column_name FROM information_schema.columns "
                        "WHERE table_name='transparency_assessment_components'"
                    )
                )
            )
            assert "rule_code" not in columns and "public_explanation" not in columns
            assert (
                historical.scalar(text("SELECT count(*) FROM transparency_assessments"))
                == historical_assessments
            )
            assert (
                historical.scalar(text("SELECT count(*) FROM transparency_observations"))
                == historical_observations
            )
            definition = historical.scalar(
                text(
                    "SELECT pg_get_functiondef"
                    "('transparency_check_history_immutable()'::regprocedure)"
                )
            )
            assert definition is not None and "PE-06A-2026-08-03" in definition
            with pytest.raises(DBAPIError, match="immutable"):
                historical.execute(text("DELETE FROM transparency_resource_checks"))
        command.upgrade(config, "0017")
        with engine.connect() as historical:
            assert not historical.scalar(
                text("SELECT to_regclass('transparency_methodologies') IS NOT NULL")
            )
            definition = historical.scalar(
                text(
                    "SELECT pg_get_functiondef"
                    "('transparency_check_history_immutable()'::regprocedure)"
                )
            )
            assert definition is not None and "PE-06A-2026-08-03" not in definition
            historical.execute(text("DELETE FROM transparency_resource_checks"))
            historical.rollback()
        command.upgrade(config, "0018")
        db.expire_all()
        rollback(db)
        load(db)
        assert load(db).unchanged > 0
        assert recalculate(db).unchanged == 5
        assert db.scalar(select(func.count()).select_from(TransparencyAssessment)) == 30
        rollback(db)
        assert db.scalar(select(func.count()).select_from(TransparencyAssessment)) == 25
