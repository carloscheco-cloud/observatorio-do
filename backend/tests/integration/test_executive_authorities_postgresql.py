import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.modules.appointments.models import Appointment, AppointmentEvidence
from app.modules.executive_authorities.loader import load_authorities, rollback_authorities
from app.modules.executive_inventory.loader import load_inventory
from app.modules.persons.models import Person, PersonEvidence
from app.modules.positions.models import Position, PositionEvidence
from tests.integration.test_postgresql_guards import migrate

pytestmark = pytest.mark.integration


def test_pe04_load_is_traceable_idempotent_and_reversible(postgres_url: str) -> None:
    migrate(postgres_url)
    with Session(create_engine(postgres_url)) as db:
        rollback_authorities(db)
        load_inventory(db)
        baseline_people = db.scalar(select(func.count()).select_from(Person)) or 0
        baseline_positions = db.scalar(select(func.count()).select_from(Position)) or 0
        baseline_appointments = db.scalar(select(func.count()).select_from(Appointment)) or 0
        preview = load_authorities(db, dry_run=True)
        assert preview.created == 75
        first = load_authorities(db)
        second = load_authorities(db)
        assert first.created == 75
        assert second.unchanged == 75
        assert db.scalar(select(func.count()).select_from(Person)) == baseline_people + 25
        assert (
            db.scalar(select(func.count()).select_from(Appointment)) == baseline_appointments + 25
        )
        assert db.scalar(select(func.count()).select_from(PersonEvidence)) == 25
        assert db.scalar(select(func.count()).select_from(PositionEvidence)) == 25
        assert db.scalar(select(func.count()).select_from(AppointmentEvidence)) == 50
        assert (
            db.scalar(
                select(func.count())
                .select_from(Appointment)
                .where(Appointment.status == "ACTIVE", Appointment.capacity == "SUBSTANTIVE")
            )
            == 25
        )
        assert db.scalar(select(func.count()).select_from(Position)) == baseline_positions + 25
        rollback_authorities(db)
        assert db.scalar(select(func.count()).select_from(Person)) == baseline_people
        assert db.scalar(select(func.count()).select_from(Appointment)) == baseline_appointments
