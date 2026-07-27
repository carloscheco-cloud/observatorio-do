import uuid
from datetime import date

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.modules.employment_relationships.models import (
    EmploymentRelationship,
    RelationshipStatus,
)
from app.modules.employment_relationships.schemas import EmploymentRelationshipCreate
from app.modules.evidence.models import Evidence
from app.modules.institutions.models import Institution
from app.modules.organizational_units.models import OrganizationalUnit
from app.modules.persons.models import Person
from app.modules.positions.models import Position
from app.modules.sources.models import Source


class InvalidEmploymentRelationship(ValueError):
    pass


def list_relationships(
    db: Session, *, person_id: uuid.UUID | None = None, institution_id: uuid.UUID | None = None
) -> list[EmploymentRelationship]:
    query = select(EmploymentRelationship)
    if person_id:
        query = query.where(EmploymentRelationship.person_id == person_id)
    if institution_id:
        query = query.where(EmploymentRelationship.institution_id == institution_id)
    return list(db.scalars(query.order_by(EmploymentRelationship.start_date.desc())))


def active_for_institution(
    db: Session, institution_id: uuid.UUID, *, as_of: date | None = None
) -> list[EmploymentRelationship]:
    target = as_of or date.today()
    return list(
        db.scalars(
            select(EmploymentRelationship).where(
                EmploymentRelationship.institution_id == institution_id,
                EmploymentRelationship.relationship_status == RelationshipStatus.ACTIVE,
                EmploymentRelationship.start_date <= target,
                or_(
                    EmploymentRelationship.end_date.is_(None),
                    EmploymentRelationship.end_date >= target,
                ),
            )
        )
    )


def overlaps(db: Session, relationship: EmploymentRelationship) -> list[EmploymentRelationship]:
    end = relationship.end_date or date.max
    return list(
        db.scalars(
            select(EmploymentRelationship).where(
                EmploymentRelationship.person_id == relationship.person_id,
                EmploymentRelationship.id != relationship.id,
                EmploymentRelationship.start_date <= end,
                or_(
                    EmploymentRelationship.end_date.is_(None),
                    EmploymentRelationship.end_date >= relationship.start_date,
                ),
            )
        )
    )


def create_relationship(
    db: Session, payload: EmploymentRelationshipCreate, *, actor_type: str = "human"
) -> EmploymentRelationship:
    if actor_type.lower() == "ai":
        raise PermissionError("AI actors cannot write canonical employment relationships")
    if db.get(Person, payload.person_id) is None:
        raise InvalidEmploymentRelationship("Person does not exist")
    if db.get(Institution, payload.institution_id) is None:
        raise InvalidEmploymentRelationship("Institution does not exist")
    if db.get(Source, payload.source_id) is None:
        raise InvalidEmploymentRelationship("Source does not exist")
    if db.get(Evidence, payload.evidence_id) is None:
        raise InvalidEmploymentRelationship("Evidence does not exist")
    evidence = db.get(Evidence, payload.evidence_id)
    if evidence and evidence.source_id != payload.source_id:
        raise InvalidEmploymentRelationship("Source must match evidence source")
    if payload.position_id is not None:
        position = db.get(Position, payload.position_id)
        if position is None:
            raise InvalidEmploymentRelationship("Position does not exist")
        if position.institution_id != payload.institution_id:
            raise InvalidEmploymentRelationship("Position belongs to another institution")
    if payload.organizational_unit_id is not None:
        unit = db.get(OrganizationalUnit, payload.organizational_unit_id)
        if unit is None:
            raise InvalidEmploymentRelationship("Organizational unit does not exist")
        if unit.institution_id != payload.institution_id:
            raise InvalidEmploymentRelationship(
                "Organizational unit belongs to another institution"
            )
    item = EmploymentRelationship(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
