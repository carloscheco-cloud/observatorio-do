import uuid
from datetime import date

from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import ColumnElement

from app.modules.appointments.models import Appointment, AppointmentStatus
from app.modules.evidence.models import Evidence
from app.modules.institutions.models import Institution
from app.modules.legal_basis.models import LegalBasis
from app.modules.organizational_units.models import (
    OrganizationalEvent,
    OrganizationalUnit,
    OrganizationalUnitEvidence,
    PositionUnitAssignment,
    UnitStatus,
)
from app.modules.organizational_units.schemas import (
    OrganizationalChartNode,
    OrganizationalEventCreate,
    OrganizationalUnitCreate,
    OrganizationalUnitRead,
)
from app.modules.positions.models import Position
from app.modules.sources.models import Source
from app.modules.territories.models import Territory


class InvalidOrganizationalUnit(ValueError):
    pass


class InvalidOrganizationalEvent(ValueError):
    pass


def _effective(target: date) -> tuple[ColumnElement[bool], ColumnElement[bool]]:
    return (
        OrganizationalUnit.valid_from <= target,
        or_(
            OrganizationalUnit.valid_to.is_(None),
            OrganizationalUnit.valid_to >= target,
        ),
    )


def list_units(
    db: Session,
    *,
    institution_id: uuid.UUID | None = None,
    as_of: date | None = None,
    active_only: bool = False,
) -> list[OrganizationalUnit]:
    statement = select(OrganizationalUnit)
    if institution_id is not None:
        statement = statement.where(OrganizationalUnit.institution_id == institution_id)
    if as_of is not None:
        statement = statement.where(*_effective(as_of))
    elif active_only:
        statement = statement.where(
            OrganizationalUnit.status == UnitStatus.CANONICAL, *_effective(date.today())
        )
    return list(
        db.scalars(
            statement.order_by(
                OrganizationalUnit.hierarchy_level,
                OrganizationalUnit.order_index,
                OrganizationalUnit.official_name,
            )
        )
    )


def get_unit(db: Session, unit_id: uuid.UUID) -> OrganizationalUnit | None:
    return db.get(OrganizationalUnit, unit_id)


def _lineage_map(db: Session, institution_id: uuid.UUID) -> dict[uuid.UUID, OrganizationalUnit]:
    return {unit.id: unit for unit in list_units(db, institution_id=institution_id)}


def ancestors(db: Session, unit_id: uuid.UUID) -> list[OrganizationalUnit]:
    unit = get_unit(db, unit_id)
    if unit is None:
        return []
    by_id = _lineage_map(db, unit.institution_id)
    result: list[OrganizationalUnit] = []
    seen = {unit.id}
    current = unit
    while current.parent_unit_id is not None:
        if current.parent_unit_id in seen or current.parent_unit_id not in by_id:
            raise InvalidOrganizationalUnit("Invalid organizational hierarchy")
        current = by_id[current.parent_unit_id]
        seen.add(current.id)
        result.append(current)
    result.reverse()
    return result


def descendants(db: Session, unit_id: uuid.UUID) -> list[OrganizationalUnit]:
    unit = get_unit(db, unit_id)
    if unit is None:
        return []
    all_units = list_units(db, institution_id=unit.institution_id)
    children: dict[uuid.UUID, list[OrganizationalUnit]] = {}
    for candidate in all_units:
        if candidate.parent_unit_id is not None:
            children.setdefault(candidate.parent_unit_id, []).append(candidate)
    result: list[OrganizationalUnit] = []
    pending = list(reversed(children.get(unit.id, [])))
    while pending:
        current = pending.pop()
        result.append(current)
        pending.extend(reversed(children.get(current.id, [])))
    return result


def path(db: Session, unit_id: uuid.UUID) -> list[OrganizationalUnit]:
    unit = get_unit(db, unit_id)
    return [] if unit is None else [*ancestors(db, unit_id), unit]


def create_unit(
    db: Session, payload: OrganizationalUnitCreate, *, actor_type: str = "human"
) -> OrganizationalUnit:
    if actor_type.lower() == "ai":
        raise PermissionError("AI actors cannot write canonical organizational units")
    if db.get(Institution, payload.institution_id) is None:
        raise InvalidOrganizationalUnit("Institution does not exist")
    if payload.parent_unit_id is not None:
        parent = db.get(OrganizationalUnit, payload.parent_unit_id)
        if parent is None:
            raise InvalidOrganizationalUnit("Parent unit does not exist")
        if parent.institution_id != payload.institution_id:
            raise InvalidOrganizationalUnit("Parent and child must belong to the same institution")
        if payload.hierarchy_level <= parent.hierarchy_level:
            raise InvalidOrganizationalUnit("Child hierarchy level must be below its parent")
    references = (
        (LegalBasis, payload.legal_basis_id, "Legal basis"),
        (Evidence, payload.evidence_id, "Evidence"),
        (Source, payload.source_id, "Source"),
        (Territory, payload.territory_id, "Territory"),
    )
    for model, identifier, label in references:
        if identifier is not None and db.get(model, identifier) is None:
            raise InvalidOrganizationalUnit(f"{label} does not exist")
    if payload.evidence_id and payload.source_id:
        evidence = db.get(Evidence, payload.evidence_id)
        if evidence is not None and evidence.source_id != payload.source_id:
            raise InvalidOrganizationalUnit("Source must be the source of the evidence")
    values = payload.model_dump(exclude={"evidence_id", "source_id"})
    item = OrganizationalUnit(**values)
    db.add(item)
    db.flush()
    if payload.evidence_id is not None and payload.source_id is not None:
        db.add(
            OrganizationalUnitEvidence(
                unit_id=item.id,
                evidence_id=payload.evidence_id,
                source_id=payload.source_id,
            )
        )
    db.commit()
    db.refresh(item)
    return item


def organizational_chart(
    db: Session, institution_id: uuid.UUID, *, as_of: date | None = None
) -> list[OrganizationalChartNode]:
    target = as_of or date.today()
    units = list_units(db, institution_id=institution_id, as_of=target)
    visible = {unit.id for unit in units}
    nodes = {
        unit.id: OrganizationalChartNode(
            **OrganizationalUnitRead.model_validate(unit).model_dump(), children=[]
        )
        for unit in units
    }
    historical_events = db.scalars(
        select(OrganizationalEvent)
        .where(
            OrganizationalEvent.institution_id == institution_id,
            OrganizationalEvent.effective_date > target,
        )
        .order_by(OrganizationalEvent.effective_date.desc())
    )
    for event in historical_events:
        node = nodes.get(event.unit_id)
        if node is None:
            continue
        if event.previous_name is not None:
            node.official_name = event.previous_name
        if event.previous_parent_id is not None or event.new_parent_id is not None:
            node.parent_unit_id = event.previous_parent_id
    roots: list[OrganizationalChartNode] = []
    for unit in units:
        node = nodes[unit.id]
        if node.parent_unit_id is None or node.parent_unit_id not in visible:
            roots.append(nodes[unit.id])
        else:
            nodes[node.parent_unit_id].children.append(nodes[unit.id])
    return roots


def positions_for_unit(db: Session, unit_id: uuid.UUID) -> list[Position]:
    return list(
        db.scalars(
            select(Position)
            .where(Position.organizational_unit_id == unit_id)
            .order_by(Position.official_name)
        )
    )


def appointments_for_unit(db: Session, unit_id: uuid.UUID) -> list[Appointment]:
    return list(
        db.scalars(
            select(Appointment)
            .join(Position, Appointment.position_id == Position.id)
            .where(Position.organizational_unit_id == unit_id)
            .order_by(Appointment.start_date.desc())
        )
    )


def units_without_head(
    db: Session, institution_id: uuid.UUID, *, as_of: date | None = None
) -> list[OrganizationalUnit]:
    target = as_of or date.today()
    headed = (
        select(Position.organizational_unit_id)
        .join(Appointment, Appointment.position_id == Position.id)
        .where(
            Position.organizational_unit_id.is_not(None),
            Appointment.status == AppointmentStatus.CONFIRMED,
            Appointment.start_date <= target,
            or_(Appointment.end_date.is_(None), Appointment.end_date >= target),
        )
    )
    return list(
        db.scalars(
            select(OrganizationalUnit)
            .where(
                OrganizationalUnit.institution_id == institution_id,
                *_effective(target),
                OrganizationalUnit.id.not_in(headed),
            )
            .order_by(OrganizationalUnit.official_name)
        )
    )


def list_events(
    db: Session, *, institution_id: uuid.UUID | None = None
) -> list[OrganizationalEvent]:
    statement = select(OrganizationalEvent)
    if institution_id is not None:
        statement = statement.where(OrganizationalEvent.institution_id == institution_id)
    return list(
        db.scalars(
            statement.order_by(
                OrganizationalEvent.effective_date.desc(), OrganizationalEvent.created_at.desc()
            )
        )
    )


def get_event(db: Session, event_id: uuid.UUID) -> OrganizationalEvent | None:
    return db.get(OrganizationalEvent, event_id)


def create_event(
    db: Session, payload: OrganizationalEventCreate, *, actor_type: str = "human"
) -> OrganizationalEvent:
    if actor_type.lower() == "ai":
        raise PermissionError("AI actors cannot write canonical organizational events")
    unit = db.get(OrganizationalUnit, payload.unit_id)
    if unit is None or unit.institution_id != payload.institution_id:
        raise InvalidOrganizationalEvent("Unit must belong to the event institution")
    for model, identifier, label in (
        (LegalBasis, payload.legal_basis_id, "Legal basis"),
        (Evidence, payload.evidence_id, "Evidence"),
        (Source, payload.source_id, "Source"),
    ):
        if db.get(model, identifier) is None:
            raise InvalidOrganizationalEvent(f"{label} does not exist")
    evidence = db.get(Evidence, payload.evidence_id)
    if evidence is not None and evidence.source_id != payload.source_id:
        raise InvalidOrganizationalEvent("Source must be the source of the evidence")
    item = OrganizationalEvent(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def add_position_assignment(
    db: Session,
    *,
    position: Position,
    unit: OrganizationalUnit,
    valid_from: date,
) -> PositionUnitAssignment:
    if position.institution_id != unit.institution_id:
        raise InvalidOrganizationalUnit("Position and unit must belong to the same institution")
    assignment = PositionUnitAssignment(
        position_id=position.id, organizational_unit_id=unit.id, valid_from=valid_from
    )
    db.add(assignment)
    return assignment
