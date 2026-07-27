import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.institutions.models import Institution
from app.modules.legal_basis.models import LegalBasis
from app.modules.organizational_units.models import OrganizationalUnit, PositionUnitAssignment
from app.modules.positions.models import Position
from app.modules.positions.schemas import PositionCreate


class InvalidPosition(ValueError):
    pass


def list_positions(db: Session) -> list[Position]:
    return list(db.scalars(select(Position).order_by(Position.code)))


def get_position(db: Session, position_id: uuid.UUID) -> Position | None:
    return db.get(Position, position_id)


def create_position(db: Session, payload: PositionCreate, *, actor_type: str = "human") -> Position:
    if actor_type.lower() == "ai":
        raise PermissionError("AI actors cannot write canonical position records")
    if db.get(Institution, payload.institution_id) is None:
        raise InvalidPosition("Institution does not exist")
    if db.get(LegalBasis, payload.legal_basis_id) is None:
        raise InvalidPosition("Legal basis does not exist")
    if payload.organizational_unit_id is not None:
        unit = db.get(OrganizationalUnit, payload.organizational_unit_id)
        if unit is None:
            raise InvalidPosition("Organizational unit does not exist")
        if unit.institution_id != payload.institution_id:
            raise InvalidPosition("Position and unit must belong to the same institution")
    item = Position(**payload.model_dump())
    db.add(item)
    db.flush()
    if payload.organizational_unit_id is not None:
        db.add(
            PositionUnitAssignment(
                position_id=item.id,
                organizational_unit_id=payload.organizational_unit_id,
                valid_from=payload.valid_from or date.today(),
            )
        )
    db.commit()
    db.refresh(item)
    return item
