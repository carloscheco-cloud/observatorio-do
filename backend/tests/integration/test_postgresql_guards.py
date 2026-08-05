import os
import uuid
from pathlib import Path

import pytest
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import DBAPIError

from alembic import command
from tests.postgres import EXPECTED_SCHEMA_REVISION

pytestmark = pytest.mark.integration

BACKEND_DIR = Path(__file__).resolve().parents[2]


def migrate(postgres_url: str) -> None:
    if os.getenv("OED_TEST_SCHEMA_VERSION") == EXPECTED_SCHEMA_REVISION:
        return
    engine = create_engine(postgres_url)
    try:
        if inspect(engine).has_table("alembic_version"):
            with engine.connect() as connection:
                if (
                    connection.scalar(text("SELECT version_num FROM alembic_version"))
                    == EXPECTED_SCHEMA_REVISION
                ):
                    return
    finally:
        engine.dispose()
    config = Config(BACKEND_DIR / "alembic.ini")
    config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    config.set_main_option("sqlalchemy.url", postgres_url)
    command.upgrade(config, "head")


def test_postgres_rejects_confirmed_institution_without_evidence(postgres_url: str) -> None:
    migrate(postgres_url)
    engine = create_engine(postgres_url)
    with engine.connect() as connection:
        transaction = connection.begin()
        territory_id = uuid.uuid4()
        try:
            connection.execute(
                text(
                    "INSERT INTO territories (id, name, code, type) "
                    "VALUES (:id, 'Prueba', :code, 'MUNICIPALITY')"
                ),
                {"id": territory_id, "code": f"TEST-{territory_id.hex[:27]}"},
            )
            with pytest.raises(DBAPIError, match="requires evidence"):
                connection.execute(
                    text(
                        "INSERT INTO institutions (id, name, kind, territory_id, status) "
                        "VALUES (:id, :name, 'test', :territory, 'CONFIRMED')"
                    ),
                    {
                        "id": uuid.uuid4(),
                        "name": f"Sin evidencia {uuid.uuid4()}",
                        "territory": territory_id,
                    },
                )
        finally:
            transaction.rollback()


def test_postgres_rejects_ai_canonical_write(postgres_url: str) -> None:
    migrate(postgres_url)
    engine = create_engine(postgres_url)
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            connection.execute(text("SET LOCAL app.actor_type = 'ai'"))
            with pytest.raises(DBAPIError, match="AI actors"):
                connection.execute(
                    text(
                        "INSERT INTO territories (id, name, code, type) "
                        "VALUES (:id, 'IA', :code, 'COUNTRY')"
                    ),
                    {"id": uuid.uuid4(), "code": f"AI-{uuid.uuid4().hex[:29]}"},
                )
        finally:
            transaction.rollback()
