import pytest
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.exc import DBAPIError

from alembic import command
from app.modules.digital_transparency.loader import load as load_pe05
from app.modules.digital_transparency.pe06b import load as load_pe06b
from app.modules.executive_authorities.loader import load_authorities
from app.modules.executive_dependencies.loader import load_dependencies
from app.modules.executive_inventory.loader import load_inventory
from tests.integration.test_postgresql_guards import BACKEND_DIR

pytestmark = pytest.mark.integration


def config(postgres_url: str) -> Config:
    item = Config(BACKEND_DIR / "alembic.ini")
    item.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    item.set_main_option("sqlalchemy.url", postgres_url)
    return item


def test_oed_td_1_1_upgrade_immutability_and_round_trip(postgres_url: str) -> None:
    migration = config(postgres_url)
    command.upgrade(migration, "0018")
    engine = create_engine(postgres_url)
    from sqlalchemy.orm import Session

    with Session(engine) as db:
        assert load_inventory(db).created > 0
        assert load_inventory(db).unchanged > 0
        assert load_dependencies(db).created > 0
        assert load_dependencies(db).unchanged > 0
        assert load_authorities(db).created > 0
        assert load_authorities(db).unchanged > 0
        assert load_pe05(db).created > 0
        assert load_pe05(db).unchanged > 0
        assert load_pe06b(db).created > 0
        assert load_pe06b(db).unchanged > 0
    with engine.connect() as connection:
        before_assessments = connection.scalar(
            text("SELECT count(*) FROM transparency_assessments")
        )
        before_observations = connection.scalar(
            text("SELECT count(*) FROM transparency_observations")
        )
        assert connection.scalar(text("SELECT count(*) FROM transparency_methodologies")) == 2
        assert connection.scalar(text("SELECT count(*) FROM transparency_scoring_rules")) == 30
        assert connection.scalar(
            text("SELECT is_immutable FROM transparency_methodologies WHERE version='OED-TD-1.0'")
        )
        assert (
            connection.scalar(text("SELECT count(*) FROM transparency_assessments"))
            == before_assessments
        )
        assert (
            connection.scalar(text("SELECT count(*) FROM transparency_observations"))
            == before_observations
        )
        with pytest.raises(DBAPIError, match="immutable"):
            connection.execute(
                text(
                    "UPDATE transparency_methodologies SET name='changed' "
                    "WHERE version='OED-TD-1.1'"
                )
            )
        connection.rollback()
        with pytest.raises(DBAPIError, match="immutable"):
            connection.execute(
                text("DELETE FROM transparency_methodologies WHERE version='OED-TD-1.1'")
            )
    command.downgrade(migration, "0017")
    with engine.connect() as connection:
        assert not connection.scalar(
            text("SELECT to_regclass('transparency_methodologies') IS NOT NULL")
        )
        columns = set(
            connection.scalars(
                text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name='transparency_assessment_components'"
                )
            )
        )
        assert "rule_code" not in columns and "public_explanation" not in columns
        assert (
            connection.scalar(text("SELECT count(*) FROM transparency_assessments"))
            == before_assessments
        )
        assert (
            connection.scalar(text("SELECT count(*) FROM transparency_observations"))
            == before_observations
        )
    command.downgrade(migration, "0016")
    with engine.connect() as connection:
        definition = connection.scalar(
            text(
                "SELECT pg_get_functiondef('transparency_check_history_immutable()'::regprocedure)"
            )
        )
        assert definition is not None and "PE-06A-2026-08-03" in definition
        assert (
            connection.scalar(text("SELECT count(*) FROM transparency_assessments"))
            == before_assessments
        )
    command.upgrade(migration, "0017")
    command.upgrade(migration, "0018")
    with engine.connect() as connection:
        assert connection.scalar(text("SELECT version_num FROM alembic_version")) == "0018"
        assert connection.scalar(text("SELECT count(*) FROM transparency_scoring_rules")) == 30
        assert connection.scalar(text("SELECT count(*) FROM transparency_methodologies")) == 2
        assert (
            connection.scalar(
                text(
                    "SELECT count(*) FROM (SELECT methodology_version, dimension, rule_code "
                    "FROM transparency_scoring_rules GROUP BY 1,2,3 HAVING count(*) > 1) duplicate"
                )
            )
            == 0
        )
        assert (
            connection.scalar(
                text(
                    "SELECT count(*) FROM transparency_scoring_rules "
                    "WHERE awarded_score < 0 OR awarded_score > maximum_score"
                )
            )
            == 0
        )
        assert (
            connection.scalar(text("SELECT count(*) FROM transparency_assessments"))
            == before_assessments
        )
        assert (
            connection.scalar(text("SELECT count(*) FROM transparency_observations"))
            == before_observations
        )
