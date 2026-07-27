import uuid
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.employment_relationships import service
from app.modules.employment_relationships.models import EmploymentRelationship
from app.modules.employment_relationships.schemas import (
    EmploymentRelationshipCreate,
    EmploymentRelationshipRead,
)

router = APIRouter(tags=["employment"])
Db = Annotated[Session, Depends(get_db)]


@router.get("/employment-relationships", response_model=list[EmploymentRelationshipRead])
def list_all(
    db: Db,
    person_id: Annotated[uuid.UUID | None, Query()] = None,
    institution_id: Annotated[uuid.UUID | None, Query()] = None,
) -> list[EmploymentRelationshipRead]:
    return [
        EmploymentRelationshipRead.model_validate(row)
        for row in service.list_relationships(
            db, person_id=person_id, institution_id=institution_id
        )
    ]


@router.post(
    "/employment-relationships",
    response_model=EmploymentRelationshipRead,
    status_code=status.HTTP_201_CREATED,
)
def create(
    payload: EmploymentRelationshipCreate,
    db: Db,
    x_actor_type: Annotated[str, Header()] = "human",
) -> EmploymentRelationshipRead:
    try:
        return EmploymentRelationshipRead.model_validate(
            service.create_relationship(db, payload, actor_type=x_actor_type)
        )
    except (ValueError, PermissionError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get(
    "/employment-relationships/{relationship_id}", response_model=EmploymentRelationshipRead
)
def get(relationship_id: uuid.UUID, db: Db) -> EmploymentRelationshipRead:
    item = db.get(EmploymentRelationship, relationship_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Employment relationship not found")
    return EmploymentRelationshipRead.model_validate(item)


@router.get(
    "/persons/{person_id}/employment-history", response_model=list[EmploymentRelationshipRead]
)
def history(person_id: uuid.UUID, db: Db) -> list[EmploymentRelationshipRead]:
    return [
        EmploymentRelationshipRead.model_validate(row)
        for row in service.list_relationships(db, person_id=person_id)
    ]


@router.get(
    "/institutions/{institution_id}/employees",
    response_model=list[EmploymentRelationshipRead],
)
def employees(institution_id: uuid.UUID, db: Db) -> list[EmploymentRelationshipRead]:
    return [
        EmploymentRelationshipRead.model_validate(row)
        for row in service.list_relationships(db, institution_id=institution_id)
    ]


@router.get(
    "/institutions/{institution_id}/active-employees",
    response_model=list[EmploymentRelationshipRead],
)
def active_employees(
    institution_id: uuid.UUID, db: Db, as_of: Annotated[date | None, Query()] = None
) -> list[EmploymentRelationshipRead]:
    return [
        EmploymentRelationshipRead.model_validate(row)
        for row in service.active_for_institution(db, institution_id, as_of=as_of)
    ]
