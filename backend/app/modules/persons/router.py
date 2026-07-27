import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.appointments.schemas import AppointmentRead
from app.modules.appointments.service import appointments_for_person
from app.modules.persons import service
from app.modules.persons.schemas import PersonCreate, PersonRead

router = APIRouter(prefix="/persons", tags=["persons"])
DatabaseSession = Annotated[Session, Depends(get_db)]
ActorType = Annotated[str, Header()]


@router.get("", response_model=list[PersonRead])
def list_all(db: DatabaseSession) -> list[PersonRead]:
    return [PersonRead.model_validate(item) for item in service.list_persons(db)]


@router.post("", response_model=PersonRead, status_code=status.HTTP_201_CREATED)
def create(
    payload: PersonCreate, db: DatabaseSession, x_actor_type: ActorType = "human"
) -> PersonRead:
    try:
        return PersonRead.model_validate(
            service.create_person(db, payload, actor_type=x_actor_type)
        )
    except PermissionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/{person_id}", response_model=PersonRead)
def get(person_id: uuid.UUID, db: DatabaseSession) -> PersonRead:
    item = service.get_person(db, person_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Person not found")
    return PersonRead.model_validate(item)


@router.get("/{person_id}/appointments", response_model=list[AppointmentRead])
def appointment_history(person_id: uuid.UUID, db: DatabaseSession) -> list[AppointmentRead]:
    if service.get_person(db, person_id) is None:
        raise HTTPException(status_code=404, detail="Person not found")
    return [AppointmentRead.model_validate(item) for item in appointments_for_person(db, person_id)]
