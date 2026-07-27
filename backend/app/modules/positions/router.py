import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.appointments.schemas import AppointmentRead
from app.modules.appointments.service import appointments_for_position
from app.modules.positions import service
from app.modules.positions.schemas import PositionCreate, PositionRead

router = APIRouter(prefix="/positions", tags=["positions"])
DatabaseSession = Annotated[Session, Depends(get_db)]
ActorType = Annotated[str, Header()]


@router.get("", response_model=list[PositionRead])
def list_all(db: DatabaseSession) -> list[PositionRead]:
    return [PositionRead.model_validate(item) for item in service.list_positions(db)]


@router.post("", response_model=PositionRead, status_code=status.HTTP_201_CREATED)
def create(
    payload: PositionCreate, db: DatabaseSession, x_actor_type: ActorType = "human"
) -> PositionRead:
    try:
        return PositionRead.model_validate(
            service.create_position(db, payload, actor_type=x_actor_type)
        )
    except (service.InvalidPosition, PermissionError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/{position_id}", response_model=PositionRead)
def get(position_id: uuid.UUID, db: DatabaseSession) -> PositionRead:
    item = service.get_position(db, position_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Position not found")
    return PositionRead.model_validate(item)


@router.get("/{position_id}/history", response_model=list[AppointmentRead])
def history(position_id: uuid.UUID, db: DatabaseSession) -> list[AppointmentRead]:
    if service.get_position(db, position_id) is None:
        raise HTTPException(status_code=404, detail="Position not found")
    return [
        AppointmentRead.model_validate(item) for item in appointments_for_position(db, position_id)
    ]
