import uuid
from datetime import date

from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import ColumnElement

from app.modules.appointments.models import Appointment, AppointmentStatus
from app.modules.appointments.schemas import AppointmentCreate
from app.modules.evidence.models import Evidence
from app.modules.institutions.models import Institution
from app.modules.persons.models import Person
from app.modules.positions.models import Position
from app.modules.sources.models import Source


class InvalidAppointment(ValueError):
    pass


def _active_on(target_date: date) -> tuple[ColumnElement[bool], ColumnElement[bool]]:
    return (
        Appointment.start_date <= target_date,
        or_(Appointment.end_date.is_(None), Appointment.end_date >= target_date),
    )


def list_appointments(db: Session) -> list[Appointment]:
    return list(db.scalars(select(Appointment).order_by(Appointment.start_date.desc())))


def active_appointments(db: Session, *, on_date: date | None = None) -> list[Appointment]:
    target = on_date or date.today()
    statement = (
        select(Appointment)
        .where(
            Appointment.status == AppointmentStatus.CONFIRMED,
            *_active_on(target),
        )
        .order_by(Appointment.start_date)
    )
    return list(db.scalars(statement))


def appointments_for_person(db: Session, person_id: uuid.UUID) -> list[Appointment]:
    statement = (
        select(Appointment)
        .where(Appointment.person_id == person_id)
        .order_by(Appointment.start_date.desc())
    )
    return list(db.scalars(statement))


def appointments_for_position(db: Session, position_id: uuid.UUID) -> list[Appointment]:
    statement = (
        select(Appointment)
        .where(Appointment.position_id == position_id)
        .order_by(Appointment.start_date.desc())
    )
    return list(db.scalars(statement))


def appointments_for_institution(
    db: Session, institution_id: uuid.UUID, *, active_only: bool = False
) -> list[Appointment]:
    statement = select(Appointment).where(Appointment.institution_id == institution_id)
    if active_only:
        statement = statement.where(
            Appointment.status == AppointmentStatus.CONFIRMED, *_active_on(date.today())
        )
    return list(db.scalars(statement.order_by(Appointment.start_date.desc())))


def create_appointment(
    db: Session, payload: AppointmentCreate, *, actor_type: str = "human"
) -> Appointment:
    if actor_type.lower() == "ai":
        raise PermissionError("AI actors cannot write canonical appointment records")
    if payload.status == AppointmentStatus.CONFIRMED:
        required = {
            "person": payload.person_id,
            "position": payload.position_id,
            "institution": payload.institution_id,
            "evidence": payload.evidence_id,
            "source": payload.source_id,
            "start_date": payload.start_date,
            "legal_act": payload.legal_act,
        }
        missing = [name for name, value in required.items() if value is None]
        if missing:
            raise InvalidAppointment(f"Confirmed appointment requires: {', '.join(missing)}")
    references = (
        (Person, payload.person_id, "Person"),
        (Position, payload.position_id, "Position"),
        (Institution, payload.institution_id, "Institution"),
        (Evidence, payload.evidence_id, "Evidence"),
        (Source, payload.source_id, "Source"),
    )
    for model, identifier, label in references:
        if identifier is not None and db.get(model, identifier) is None:
            raise InvalidAppointment(f"{label} does not exist")
    if payload.position_id and payload.institution_id:
        position = db.get(Position, payload.position_id)
        if position is not None and position.institution_id != payload.institution_id:
            raise InvalidAppointment("Appointment institution must match position institution")
    if payload.evidence_id and payload.source_id:
        evidence = db.get(Evidence, payload.evidence_id)
        if evidence is not None and evidence.source_id != payload.source_id:
            raise InvalidAppointment("Appointment source must be the source of its evidence")
    item = Appointment(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
