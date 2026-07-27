import uuid
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.appointments.schemas import AppointmentRead
from app.modules.institutions.models import Institution
from app.modules.organizational_units import service
from app.modules.organizational_units.schemas import (
    OrganizationalChartNode,
    OrganizationalEventCreate,
    OrganizationalEventRead,
    OrganizationalUnitCreate,
    OrganizationalUnitRead,
)
from app.modules.positions.schemas import PositionRead

router = APIRouter(tags=["organizational structure"])
DatabaseSession = Annotated[Session, Depends(get_db)]
ActorType = Annotated[str, Header()]


def _require_unit(db: Session, unit_id: uuid.UUID) -> None:
    if service.get_unit(db, unit_id) is None:
        raise HTTPException(status_code=404, detail="Organizational unit not found")


@router.get("/organizational-units", response_model=list[OrganizationalUnitRead])
def list_all(
    db: DatabaseSession,
    institution_id: uuid.UUID | None = None,
    as_of: date | None = None,
    active_only: bool = False,
) -> list[OrganizationalUnitRead]:
    return [
        OrganizationalUnitRead.model_validate(item)
        for item in service.list_units(
            db, institution_id=institution_id, as_of=as_of, active_only=active_only
        )
    ]


@router.post(
    "/organizational-units",
    response_model=OrganizationalUnitRead,
    status_code=status.HTTP_201_CREATED,
)
def create_unit(
    payload: OrganizationalUnitCreate,
    db: DatabaseSession,
    x_actor_type: ActorType = "human",
) -> OrganizationalUnitRead:
    try:
        return OrganizationalUnitRead.model_validate(
            service.create_unit(db, payload, actor_type=x_actor_type)
        )
    except (service.InvalidOrganizationalUnit, PermissionError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/organizational-units/{unit_id}", response_model=OrganizationalUnitRead)
def get_unit(unit_id: uuid.UUID, db: DatabaseSession) -> OrganizationalUnitRead:
    item = service.get_unit(db, unit_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Organizational unit not found")
    return OrganizationalUnitRead.model_validate(item)


@router.get(
    "/organizational-units/{unit_id}/ancestors",
    response_model=list[OrganizationalUnitRead],
)
def ancestors(unit_id: uuid.UUID, db: DatabaseSession) -> list[OrganizationalUnitRead]:
    _require_unit(db, unit_id)
    return [OrganizationalUnitRead.model_validate(item) for item in service.ancestors(db, unit_id)]


@router.get(
    "/organizational-units/{unit_id}/descendants",
    response_model=list[OrganizationalUnitRead],
)
def descendants(unit_id: uuid.UUID, db: DatabaseSession) -> list[OrganizationalUnitRead]:
    _require_unit(db, unit_id)
    return [
        OrganizationalUnitRead.model_validate(item) for item in service.descendants(db, unit_id)
    ]


@router.get("/organizational-units/{unit_id}/path", response_model=list[OrganizationalUnitRead])
def hierarchy_path(unit_id: uuid.UUID, db: DatabaseSession) -> list[OrganizationalUnitRead]:
    _require_unit(db, unit_id)
    return [OrganizationalUnitRead.model_validate(item) for item in service.path(db, unit_id)]


@router.get("/organizational-units/{unit_id}/positions", response_model=list[PositionRead])
def positions(unit_id: uuid.UUID, db: DatabaseSession) -> list[PositionRead]:
    _require_unit(db, unit_id)
    return [PositionRead.model_validate(item) for item in service.positions_for_unit(db, unit_id)]


@router.get("/organizational-units/{unit_id}/appointments", response_model=list[AppointmentRead])
def appointments(unit_id: uuid.UUID, db: DatabaseSession) -> list[AppointmentRead]:
    _require_unit(db, unit_id)
    return [
        AppointmentRead.model_validate(item) for item in service.appointments_for_unit(db, unit_id)
    ]


@router.get(
    "/institutions/{institution_id}/organizational-units",
    response_model=list[OrganizationalUnitRead],
)
def institution_units(
    institution_id: uuid.UUID, db: DatabaseSession, as_of: date | None = None
) -> list[OrganizationalUnitRead]:
    if db.get(Institution, institution_id) is None:
        raise HTTPException(status_code=404, detail="Institution not found")
    return [
        OrganizationalUnitRead.model_validate(item)
        for item in service.list_units(db, institution_id=institution_id, as_of=as_of)
    ]


@router.get(
    "/institutions/{institution_id}/organizational-chart",
    response_model=list[OrganizationalChartNode],
)
def chart(
    institution_id: uuid.UUID, db: DatabaseSession, as_of: date | None = None
) -> list[OrganizationalChartNode]:
    if db.get(Institution, institution_id) is None:
        raise HTTPException(status_code=404, detail="Institution not found")
    return service.organizational_chart(db, institution_id, as_of=as_of)


@router.get(
    "/institutions/{institution_id}/units-without-head",
    response_model=list[OrganizationalUnitRead],
)
def without_head(
    institution_id: uuid.UUID, db: DatabaseSession, as_of: date | None = None
) -> list[OrganizationalUnitRead]:
    return [
        OrganizationalUnitRead.model_validate(item)
        for item in service.units_without_head(db, institution_id, as_of=as_of)
    ]


@router.get("/organizational-events", response_model=list[OrganizationalEventRead])
def events(
    db: DatabaseSession, institution_id: uuid.UUID | None = None
) -> list[OrganizationalEventRead]:
    return [
        OrganizationalEventRead.model_validate(item)
        for item in service.list_events(db, institution_id=institution_id)
    ]


@router.post(
    "/organizational-events",
    response_model=OrganizationalEventRead,
    status_code=status.HTTP_201_CREATED,
)
def create_event(
    payload: OrganizationalEventCreate,
    db: DatabaseSession,
    x_actor_type: ActorType = "human",
) -> OrganizationalEventRead:
    try:
        return OrganizationalEventRead.model_validate(
            service.create_event(db, payload, actor_type=x_actor_type)
        )
    except (service.InvalidOrganizationalEvent, PermissionError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/organizational-events/{event_id}", response_model=OrganizationalEventRead)
def event(event_id: uuid.UUID, db: DatabaseSession) -> OrganizationalEventRead:
    item = service.get_event(db, event_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Organizational event not found")
    return OrganizationalEventRead.model_validate(item)
