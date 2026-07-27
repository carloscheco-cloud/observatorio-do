import uuid

import pytest
from sqlalchemy import create_engine, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from app.db.seed import seed
from app.modules.payroll_entries.models import PayrollEntry
from tests.integration.test_postgresql_guards import migrate

pytestmark = pytest.mark.integration


def _seeded(postgres_url: str) -> tuple[object, PayrollEntry]:
    migrate(postgres_url)
    engine = create_engine(postgres_url)
    with Session(engine) as db:
        seed(db)
        entry = db.scalar(select(PayrollEntry))
        assert entry is not None
        db.expunge(entry)
    return engine, entry


def test_postgres_rejects_negative_payroll_amount(postgres_url: str) -> None:
    engine, entry = _seeded(postgres_url)
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            with pytest.raises(DBAPIError, match="ck_payroll_entry_amounts"):
                connection.execute(
                    text("UPDATE payroll_entries SET gross_income=-1 WHERE id=:id"),
                    {"id": entry.id},
                )
        finally:
            transaction.rollback()


def test_postgres_rejects_sensitive_identifier_and_ai_actor(postgres_url: str) -> None:
    engine, entry = _seeded(postgres_url)
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            with pytest.raises(DBAPIError, match="national identifier"):
                connection.execute(
                    text(
                        "UPDATE payroll_entries "
                        "SET listed_name='Control 001-1234567-8' WHERE id=:id"
                    ),
                    {"id": entry.id},
                )
        finally:
            transaction.rollback()
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            connection.execute(text("SET LOCAL app.actor_type = 'ai'"))
            with pytest.raises(DBAPIError, match="AI actors"):
                connection.execute(
                    text("UPDATE payroll_entries SET row_number=:row WHERE id=:id"),
                    {"row": uuid.uuid4().int % 1000 + 1, "id": entry.id},
                )
        finally:
            transaction.rollback()


def test_postgres_rejects_period_institution_mismatch(postgres_url: str) -> None:
    engine, entry = _seeded(postgres_url)
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            with pytest.raises(DBAPIError, match="must match payroll period"):
                connection.execute(
                    text("UPDATE payroll_entries SET institution_id=:other WHERE id=:id"),
                    {"other": uuid.uuid4(), "id": entry.id},
                )
        finally:
            transaction.rollback()
