from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.appointments import service
from app.modules.appointments.schemas import AppointmentCreate, AppointmentRead

router = APIRouter(prefix="/appointments", tags=["appointments"])
DatabaseSession = Annotated[Session, Depends(get_db)]
ActorType = Annotated[str, Header()]


@router.get("", response_model=list[AppointmentRead])
def list_all(db: DatabaseSession) -> list[AppointmentRead]:
    return [AppointmentRead.model_validate(item) for item in service.list_appointments(db)]


@router.post("", response_model=AppointmentRead, status_code=status.HTTP_201_CREATED)
def create(
    payload: AppointmentCreate, db: DatabaseSession, x_actor_type: ActorType = "human"
) -> AppointmentRead:
    try:
        return AppointmentRead.model_validate(
            service.create_appointment(db, payload, actor_type=x_actor_type)
        )
    except (service.InvalidAppointment, PermissionError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/active", response_model=list[AppointmentRead])
def active(
    db: DatabaseSession, on_date: Annotated[date | None, Query()] = None
) -> list[AppointmentRead]:
    return [
        AppointmentRead.model_validate(item)
        for item in service.active_appointments(db, on_date=on_date)
    ]
