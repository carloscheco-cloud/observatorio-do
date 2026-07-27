from datetime import date

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.seed import seed
from app.modules.appointments.models import Appointment, AppointmentStatus
from app.modules.appointments.schemas import AppointmentCreate
from app.modules.appointments.service import (
    InvalidAppointment,
    active_appointments,
    appointments_for_person,
    appointments_for_position,
    create_appointment,
)
from app.modules.persons.models import Person
from app.modules.persons.schemas import PersonCreate
from app.modules.persons.service import create_person, normalize_name
from app.modules.positions.models import Position


def test_person_name_is_normalized_and_plain_national_id_is_rejected(db: Session) -> None:
    person = create_person(db, PersonCreate(full_name="  Ána   Núñez  "))
    assert person.normalized_name == "ana nunez"
    with pytest.raises(ValueError, match="64 characters"):
        PersonCreate(full_name="Otra Persona", national_id_hash="00112345678")


def test_ai_cannot_write_block_3_canonical_records(db: Session) -> None:
    with pytest.raises(PermissionError):
        create_person(db, PersonCreate(full_name="Propuesta IA"), actor_type="ai")


def test_confirmed_appointment_requires_traceability(db: Session) -> None:
    with pytest.raises(InvalidAppointment, match="person"):
        create_appointment(
            db,
            AppointmentCreate(
                appointment_type="test",
                status=AppointmentStatus.CONFIRMED,
            ),
        )


def test_historical_queries_and_point_in_time(db: Session) -> None:
    seed(db)
    person = db.scalar(select(Person))
    position = db.scalar(select(Position))
    appointment = db.scalar(select(Appointment))
    assert person is not None
    assert position is not None
    assert appointment is not None
    assert appointments_for_person(db, person.id) == [appointment]
    assert appointments_for_position(db, position.id) == [appointment]
    assert active_appointments(db, on_date=date(2025, 6, 1)) == [appointment]
    assert active_appointments(db, on_date=date(2024, 12, 31)) == []


def test_normalize_name_is_deterministic() -> None:
    assert normalize_name("José  DE la Cruz") == "jose de la cruz"
