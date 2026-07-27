import uuid

import pytest
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.exc import DBAPIError

from alembic import command

pytestmark = pytest.mark.integration


def migrate(postgres_url: str) -> None:
    config = Config("backend/alembic.ini")
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
                {"id": territory_id, "code": f"TEST-{territory_id}"},
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
                    {"id": uuid.uuid4(), "code": f"AI-{uuid.uuid4()}"},
                )
        finally:
            transaction.rollback()
