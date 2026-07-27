import uuid

import pytest
from alembic.config import Config
from sqlalchemy import create_engine, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from app.db.seed import seed
from app.modules.appointments.models import Appointment
from app.modules.persons.models import Person
from app.modules.positions.models import Position
from tests.integration.test_postgresql_guards import BACKEND_DIR, migrate

pytestmark = pytest.mark.integration


def test_alembic_has_one_head() -> None:
    from alembic.script import ScriptDirectory

    config = Config(BACKEND_DIR / "alembic.ini")
    config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    assert len(ScriptDirectory.from_config(config).get_heads()) == 1


def test_block_3_seed_is_idempotent_on_postgresql(postgres_url: str) -> None:
    migrate(postgres_url)
    engine = create_engine(postgres_url)
    with Session(engine) as db:
        seed(db)
        seed(db)
        assert len(list(db.scalars(select(Person)))) == 1
        assert len(list(db.scalars(select(Position)))) == 1
        assert len(list(db.scalars(select(Appointment)))) == 1


def test_postgres_rejects_incomplete_confirmed_appointment(postgres_url: str) -> None:
    migrate(postgres_url)
    engine = create_engine(postgres_url)
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            with pytest.raises(DBAPIError, match="ck_confirmed_appointment_complete"):
                connection.execute(
                    text(
                        "INSERT INTO appointments "
                        "(id, appointment_type, status, metadata) "
                        "VALUES (:id, 'test', 'CONFIRMED', '{}')"
                    ),
                    {"id": uuid.uuid4()},
                )
        finally:
            transaction.rollback()


def test_postgres_rejects_ai_person_write(postgres_url: str) -> None:
    migrate(postgres_url)
    engine = create_engine(postgres_url)
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            connection.execute(text("SET LOCAL app.actor_type = 'ai'"))
            with pytest.raises(DBAPIError, match="AI actors"):
                connection.execute(
                    text(
                        "INSERT INTO persons "
                        "(id, full_name, normalized_name, status, metadata) "
                        "VALUES (:id, 'Persona IA', 'persona ia', 'DRAFT', '{}')"
                    ),
                    {"id": uuid.uuid4()},
                )
        finally:
            transaction.rollback()


def test_postgres_rejects_overlapping_single_occupant_appointment(
    postgres_url: str,
) -> None:
    migrate(postgres_url)
    engine = create_engine(postgres_url)
    with Session(engine) as db:
        seed(db)
        original = db.scalar(select(Appointment))
        assert original is not None
        second_person = Person(
            full_name="Segunda Persona Ficticia",
            normalized_name="segunda persona ficticia",
            metadata_={"controlled": True},
        )
        db.add(second_person)
        db.commit()
        with pytest.raises(DBAPIError, match="Single-occupant"):
            db.execute(
                text(
                    "INSERT INTO appointments "
                    "(id, person_id, position_id, institution_id, start_date, "
                    "appointment_type, status, legal_act, evidence_id, source_id, metadata) "
                    "VALUES (:id, :person, :position, :institution, '2026-01-01', "
                    "'controlled_test', 'CONFIRMED', 'ACTO-CONTROL-B3-002', "
                    ":evidence, :source, '{}')"
                ),
                {
                    "id": uuid.uuid4(),
                    "person": second_person.id,
                    "position": original.position_id,
                    "institution": original.institution_id,
                    "evidence": original.evidence_id,
                    "source": original.source_id,
                },
            )
            db.commit()
        db.rollback()
