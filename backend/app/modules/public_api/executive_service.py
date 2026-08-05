import math
import re
import uuid
from datetime import UTC, date, datetime, time
from typing import Any

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, aliased

from app.modules.appointments.models import Appointment, AppointmentEvidence, AppointmentStatus
from app.modules.digital_transparency.models import (
    AssessmentComponent,
    DocumentRequirement,
    DocumentResource,
    TransparencyAssessment,
    TransparencyMethodology,
    TransparencyObservation,
)
from app.modules.evidence.models import Evidence
from app.modules.institutions.models import (
    Institution,
    InstitutionEvidence,
    InstitutionRelationship,
    InstitutionStatus,
    InstitutionType,
    OperationalStatus,
    StateBranch,
)
from app.modules.legal_basis.models import LegalBasis
from app.modules.persons.models import Person, PersonStatus
from app.modules.positions.models import Position, PositionStatus
from app.modules.sources.models import Source

PUBLIC_LIMITATION = (
    "Los datos reflejan únicamente fuentes oficiales localizadas y verificadas; la ausencia de "
    "información significa no disponible, no cero ni inexistencia."
)
SCORE_LIMITATION = (
    "La puntuación mide disponibilidad y calidad documental; no mide corrupción, honestidad, "
    "legalidad ni desempeño político."
)
CURRENT_STATUSES = (AppointmentStatus.ACTIVE, AppointmentStatus.CONFIRMED)
PUBLIC_EXECUTIVE_TYPES = (
    InstitutionType.PRESIDENCY,
    InstitutionType.VICE_PRESIDENCY,
    InstitutionType.MINISTRY,
)


def _executive_scope() -> tuple[Any, ...]:
    return (
        Institution.status == InstitutionStatus.CONFIRMED,
        Institution.state_branch == StateBranch.EXECUTIVE,
        Institution.institution_type.in_(PUBLIC_EXECUTIVE_TYPES),
    )


def _enum(value: Any) -> str:
    return str(value.value if hasattr(value, "value") else value)


def _ref(row: Institution) -> dict[str, Any]:
    return {"id": str(row.id), "slug": row.slug or str(row.id), "official_name": row.name}


def _evidence(row: Evidence, source: Source) -> dict[str, Any]:
    locator = row.locator
    if re.match(r"^(?:[a-zA-Z]:[\\/]|file:|/)", locator):
        locator = source.url
    return {
        "id": str(row.id),
        "title": row.title,
        "locator": locator,
        "observed_at": row.observed_at,
        "source_name": source.name,
        "source_url": source.url,
        "official_source": source.is_official,
    }


def _pages(total: int, size: int) -> int:
    return math.ceil(total / size) if total else 0


def _act_located(appointment: Appointment) -> bool:
    return bool(appointment.legal_act or appointment.decree_number or appointment.legal_act_url)


def _institution(db: Session, slug: str) -> Institution | None:
    return db.scalar(
        select(Institution).where(
            Institution.slug == slug,
            *_executive_scope(),
        )
    )


def _latest_assessment_subquery() -> Any:
    return (
        select(
            TransparencyAssessment.id.label("assessment_id"),
            func.row_number()
            .over(
                partition_by=TransparencyAssessment.institution_id,
                order_by=(
                    TransparencyAssessment.assessment_date.desc(),
                    TransparencyAssessment.coverage_percentage.desc(),
                    TransparencyAssessment.methodology_version.desc(),
                    TransparencyAssessment.id.desc(),
                ),
            )
            .label("rn"),
        )
        .join(Institution, TransparencyAssessment.institution_id == Institution.id)
        .where(*_executive_scope())
        .subquery()
    )


def summary(db: Session) -> dict[str, Any]:
    inst = and_(*_executive_scope())
    latest = _latest_assessment_subquery()
    current = and_(
        Appointment.status.in_(CURRENT_STATUSES),
        or_(Appointment.end_date.is_(None), Appointment.end_date >= date.today()),
    )
    update_values = [
        value
        for value in (
            db.scalar(select(func.max(Institution.last_reviewed_at)).where(inst)),
            db.scalar(
                select(func.max(Appointment.updated_at))
                .join(Institution, Appointment.institution_id == Institution.id)
                .where(inst)
            ),
            db.scalar(
                select(func.max(TransparencyAssessment.assessment_date))
                .join(Institution)
                .where(inst)
            ),
        )
        if value is not None
    ]
    normalized_updates = []
    for value in update_values:
        if isinstance(value, date) and not isinstance(value, datetime):
            normalized_updates.append(datetime.combine(value, time.min, UTC))
        elif isinstance(value, datetime) and value.tzinfo is None:
            normalized_updates.append(value.replace(tzinfo=UTC))
        else:
            normalized_updates.append(value)
    latest_update = max(normalized_updates, default=None)
    return {
        "total_institutions": db.scalar(select(func.count()).select_from(Institution).where(inst))
        or 0,
        "total_active_institutions": db.scalar(
            select(func.count())
            .select_from(Institution)
            .where(inst, Institution.operational_status == OperationalStatus.ACTIVE)
        )
        or 0,
        "total_ministries": db.scalar(
            select(func.count())
            .select_from(Institution)
            .where(inst, Institution.institution_type == InstitutionType.MINISTRY)
        )
        or 0,
        "presidency_present": bool(
            db.scalar(
                select(func.count())
                .select_from(Institution)
                .where(inst, Institution.institution_type == InstitutionType.PRESIDENCY)
            )
        ),
        "vice_presidency_present": bool(
            db.scalar(
                select(func.count())
                .select_from(Institution)
                .where(inst, Institution.institution_type == InstitutionType.VICE_PRESIDENCY)
            )
        ),
        "total_current_authorities": db.scalar(
            select(func.count())
            .select_from(Appointment)
            .join(Institution, Appointment.institution_id == Institution.id)
            .where(inst, current)
        )
        or 0,
        "total_relationships": db.scalar(
            select(func.count())
            .select_from(InstitutionRelationship)
            .join(Institution, InstitutionRelationship.parent_institution_id == Institution.id)
            .where(inst)
        )
        or 0,
        "institutions_with_transparency_assessment": db.scalar(
            select(func.count()).select_from(latest).where(latest.c.rn == 1)
        )
        or 0,
        "institutions_with_complete_assessment": db.scalar(
            select(func.count())
            .select_from(TransparencyAssessment)
            .join(
                latest, and_(latest.c.assessment_id == TransparencyAssessment.id, latest.c.rn == 1)
            )
            .where(TransparencyAssessment.maturity_status == "complete")
        )
        or 0,
        "institutions_with_partial_assessment": db.scalar(
            select(func.count())
            .select_from(TransparencyAssessment)
            .join(
                latest, and_(latest.c.assessment_id == TransparencyAssessment.id, latest.c.rn == 1)
            )
            .where(TransparencyAssessment.maturity_status == "partial")
        )
        or 0,
        "latest_data_update": latest_update,
        "methodology_versions": list(
            db.scalars(
                select(TransparencyMethodology.version)
                .where(TransparencyMethodology.status == "published")
                .order_by(TransparencyMethodology.version)
            )
        ),
        "ranking_enabled": False,
        "data_scope": "Poder Ejecutivo dominicano documentado en PE-01 a PE-06D.",
        "limitations": [
            PUBLIC_LIMITATION,
            SCORE_LIMITATION,
            "Cobertura completa significa cobertura metodológica completa, "
            "no ausencia de deficiencias.",
        ],
    }


def _authority_rows(
    db: Session, institution_ids: list[uuid.UUID]
) -> dict[uuid.UUID, tuple[Any, ...]]:
    if not institution_ids:
        return {}
    rows = db.execute(
        select(Appointment, Person, Position)
        .join(Person, Appointment.person_id == Person.id)
        .join(Position, Appointment.position_id == Position.id)
        .where(
            Appointment.institution_id.in_(institution_ids),
            Appointment.status.in_(CURRENT_STATUSES),
            or_(Appointment.end_date.is_(None), Appointment.end_date >= date.today()),
            Person.status == PersonStatus.CONFIRMED,
            Position.status == PositionStatus.CANONICAL,
        )
        .order_by(Appointment.institution_id, Appointment.start_date.desc().nullslast())
    )
    result: dict[uuid.UUID, tuple[Any, ...]] = {}
    for appointment, person, position in rows:
        result.setdefault(appointment.institution_id, (appointment, person, position))
    return result


def _assessment_rows(
    db: Session, institution_ids: list[uuid.UUID]
) -> dict[uuid.UUID, TransparencyAssessment]:
    if not institution_ids:
        return {}
    rows = db.scalars(
        select(TransparencyAssessment)
        .where(TransparencyAssessment.institution_id.in_(institution_ids))
        .order_by(
            TransparencyAssessment.institution_id,
            TransparencyAssessment.assessment_date.desc(),
            TransparencyAssessment.coverage_percentage.desc(),
            TransparencyAssessment.methodology_version.desc(),
            TransparencyAssessment.id.desc(),
        )
    )
    result: dict[uuid.UUID, TransparencyAssessment] = {}
    for row in rows:
        result.setdefault(row.institution_id, row)
    return result


def list_institutions(
    db: Session,
    *,
    page: int,
    page_size: int,
    search: str | None,
    institution_type: str | None,
    parent_slug: str | None,
    has_current_authority: bool | None,
    has_transparency_assessment: bool | None,
    maturity_status: str | None,
    sort_by: str,
    sort_order: str,
) -> dict[str, Any]:
    conditions = list(_executive_scope())
    if search:
        conditions.append(
            or_(
                Institution.name.ilike(f"%{search.strip()}%"),
                Institution.acronym.ilike(f"%{search.strip()}%"),
            )
        )
    if institution_type:
        conditions.append(Institution.institution_type == institution_type)
    if parent_slug:
        parent = aliased(Institution)
        conditions.append(
            Institution.id.in_(
                select(InstitutionRelationship.child_institution_id)
                .join(parent, InstitutionRelationship.parent_institution_id == parent.id)
                .where(parent.slug == parent_slug, InstitutionRelationship.valid_to.is_(None))
            )
        )
    current_exists = (
        select(Appointment.id)
        .where(
            Appointment.institution_id == Institution.id,
            Appointment.status.in_(CURRENT_STATUSES),
            or_(Appointment.end_date.is_(None), Appointment.end_date >= date.today()),
        )
        .exists()
    )
    assess_exists = (
        select(TransparencyAssessment.id)
        .where(TransparencyAssessment.institution_id == Institution.id)
        .exists()
    )
    if has_current_authority is not None:
        conditions.append(current_exists if has_current_authority else ~current_exists)
    if has_transparency_assessment is not None:
        conditions.append(assess_exists if has_transparency_assessment else ~assess_exists)
    if maturity_status:
        latest_maturity = (
            select(TransparencyAssessment.maturity_status)
            .where(TransparencyAssessment.institution_id == Institution.id)
            .order_by(
                TransparencyAssessment.assessment_date.desc(),
                TransparencyAssessment.coverage_percentage.desc(),
                TransparencyAssessment.methodology_version.desc(),
                TransparencyAssessment.id.desc(),
            )
            .limit(1)
            .scalar_subquery()
        )
        conditions.append(latest_maturity == maturity_status)
    total = db.scalar(select(func.count()).select_from(Institution).where(*conditions)) or 0
    sort_columns = {
        "official_name": Institution.name,
        "institution_type": Institution.institution_type,
        "updated_at": Institution.last_reviewed_at,
        "transparency_score": (
            select(TransparencyAssessment.normalized_score)
            .where(TransparencyAssessment.institution_id == Institution.id)
            .order_by(
                TransparencyAssessment.assessment_date.desc(),
                TransparencyAssessment.coverage_percentage.desc(),
                TransparencyAssessment.methodology_version.desc(),
                TransparencyAssessment.id.desc(),
            )
            .limit(1)
            .scalar_subquery()
        ),
        "transparency_coverage": (
            select(TransparencyAssessment.coverage_percentage)
            .where(TransparencyAssessment.institution_id == Institution.id)
            .order_by(
                TransparencyAssessment.assessment_date.desc(),
                TransparencyAssessment.coverage_percentage.desc(),
                TransparencyAssessment.methodology_version.desc(),
                TransparencyAssessment.id.desc(),
            )
            .limit(1)
            .scalar_subquery()
        ),
    }
    sort_column = sort_columns.get(sort_by, Institution.name)
    rows = list(
        db.scalars(
            select(Institution)
            .where(*conditions)
            .order_by(
                sort_column.desc().nullslast()
                if sort_order == "desc"
                else sort_column.asc().nullslast(),
                Institution.id,
            )
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
    )
    ids = [row.id for row in rows]
    authorities = _authority_rows(db, ids)
    assessments = _assessment_rows(db, ids)
    source_counts: dict[uuid.UUID, int] = (
        {
            institution_id: count
            for institution_id, count in db.execute(
                select(
                    InstitutionEvidence.institution_id,
                    func.count(func.distinct(Evidence.source_id)),
                )
                .join(Evidence, InstitutionEvidence.evidence_id == Evidence.id)
                .where(InstitutionEvidence.institution_id.in_(ids))
                .group_by(InstitutionEvidence.institution_id)
            )
        }
        if ids
        else {}
    )
    parent_rows: Any = (
        db.execute(
            select(InstitutionRelationship.child_institution_id, Institution)
            .join(Institution, InstitutionRelationship.parent_institution_id == Institution.id)
            .where(
                InstitutionRelationship.child_institution_id.in_(ids),
                InstitutionRelationship.valid_to.is_(None),
            )
        )
        if ids
        else []
    )
    parents = {child_id: parent for child_id, parent in parent_rows}
    items = []
    for row in rows:
        authority = authorities.get(row.id)
        assessment = assessments.get(row.id)
        items.append(
            {
                "id": str(row.id),
                "slug": row.slug or str(row.id),
                "official_name": row.name,
                "short_name": row.acronym,
                "institution_type": _enum(row.institution_type or row.kind),
                "status": _enum(row.operational_status),
                "parent_institution": _ref(parents[row.id]) if row.id in parents else None,
                "official_website": row.official_website,
                "current_authority_summary": None
                if not authority
                else {
                    "appointment_id": str(authority[0].id),
                    "person_id": str(authority[1].id),
                    "public_name": authority[1].full_name,
                    "position": authority[2].official_name,
                    "appointment_status": _enum(authority[0].status),
                },
                "latest_transparency_summary": _assessment_summary(assessment)
                if assessment
                else None,
                "source_count": source_counts.get(row.id, 0),
                "last_verified_at": row.last_reviewed_at,
            }
        )
    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": _pages(total, page_size),
    }


def _assessment_summary(row: TransparencyAssessment) -> dict[str, Any]:
    return {
        "assessment_id": str(row.id),
        "assessment_date": row.assessment_date,
        "methodology_version": row.methodology_version,
        "normalized_score": row.normalized_score,
        "coverage_percentage": row.coverage_percentage,
        "maturity_status": row.maturity_status,
    }


def _evidence_map(db: Session, ids: set[uuid.UUID]) -> dict[uuid.UUID, dict[str, Any]]:
    if not ids:
        return {}
    return {
        e.id: _evidence(e, s)
        for e, s in db.execute(
            select(Evidence, Source)
            .join(Source, Evidence.source_id == Source.id)
            .where(Evidence.id.in_(ids))
        )
    }


def authority_for_institution(db: Session, institution: Institution) -> dict[str, Any] | None:
    row = _authority_rows(db, [institution.id]).get(institution.id)
    if not row:
        return None
    appointment, person, position = row
    return _appointment_public(db, appointment, person, position, institution)


def _appointment_public(
    db: Session,
    appointment: Appointment,
    person: Person,
    position: Position,
    institution: Institution,
) -> dict[str, Any]:
    links = list(
        db.execute(
            select(AppointmentEvidence.relation, AppointmentEvidence.evidence_id).where(
                AppointmentEvidence.appointment_id == appointment.id
            )
        )
    )
    ev = _evidence_map(
        db,
        {item[1] for item in links}
        | ({appointment.evidence_id} if appointment.evidence_id else set()),
    )
    appointment_evidence = [
        ev[eid] for relation, eid in links if relation == "supports_appointment" and eid in ev
    ]
    current_evidence = [
        ev[eid] for relation, eid in links if relation == "supports_current_status" and eid in ev
    ]
    act_located = _act_located(appointment)
    limitations = [PUBLIC_LIMITATION]
    if not act_located:
        limitations.append(
            "El acto de designación no fue localizado en las fuentes revisadas; "
            "esto no demuestra que no exista."
        )
    return {
        "appointment_id": str(appointment.id),
        "person_id": str(person.id),
        "public_name": person.full_name,
        "position": position.official_name,
        "position_type": position.position_type,
        "institution": _ref(institution),
        "capacity": _enum(appointment.capacity) if appointment.capacity else None,
        "appointment_status": _enum(appointment.status),
        "start_date": appointment.start_date,
        "end_date": appointment.end_date,
        "appointment_act": appointment.legal_act,
        "appointment_mechanism": _enum(appointment.mechanism) if appointment.mechanism else None,
        "act_located": act_located,
        "appointment_evidence": appointment_evidence,
        "current_status_evidence": current_evidence,
        "verification_level": "verified"
        if appointment_evidence and current_evidence
        else "partially_verified",
        "limitations": limitations,
    }


def relationships(
    db: Session, institution: Institution, direction: str = "all"
) -> list[dict[str, Any]]:
    conditions = []
    if direction in ("all", "incoming"):
        conditions.append(InstitutionRelationship.child_institution_id == institution.id)
    if direction in ("all", "outgoing"):
        conditions.append(InstitutionRelationship.parent_institution_id == institution.id)
    if not conditions:
        return []
    # Explicit joins avoid ORM relationship loading and N+1.
    Parent = aliased(Institution)
    Child = aliased(Institution)
    rows = list(
        db.execute(
            select(InstitutionRelationship, Parent, Child)
            .join(Parent, InstitutionRelationship.parent_institution_id == Parent.id)
            .join(Child, InstitutionRelationship.child_institution_id == Child.id)
            .where(or_(*conditions))
            .order_by(InstitutionRelationship.created_at.desc())
        )
    )
    ev = _evidence_map(db, {r.evidence_id for r, _, _ in rows})
    result = []
    for rel, parent, child in rows:
        rel_direction = "outgoing" if rel.parent_institution_id == institution.id else "incoming"
        result.append(
            {
                "id": str(rel.id),
                "direction": rel_direction,
                "source_institution": _ref(parent),
                "target_institution": _ref(child),
                "relationship_type": _enum(rel.relationship_type),
                "valid_from": rel.valid_from,
                "valid_to": rel.valid_to,
                "is_current": rel.valid_to is None or rel.valid_to >= date.today(),
                "evidence": ev[rel.evidence_id],
                "legal_basis": [],
                "verification_status": "verified_with_evidence",
            }
        )
    return result


def legal_basis(db: Session, institution: Institution) -> list[dict[str, Any]]:
    ids = set(
        db.scalars(select(Position.legal_basis_id).where(Position.institution_id == institution.id))
    )
    ids.update(
        db.scalars(
            select(DocumentRequirement.legal_basis_id)
            .join(DocumentResource, DocumentResource.requirement_id == DocumentRequirement.id)
            .where(
                DocumentResource.institution_id == institution.id,
                DocumentRequirement.legal_basis_id.is_not(None),
            )
        )
    )
    rows = list(db.scalars(select(LegalBasis).where(LegalBasis.id.in_(ids)))) if ids else []
    ev = _evidence_map(db, {row.evidence_id for row in rows})
    resources = (
        {
            lb_id: searchable
            for lb_id, searchable in db.execute(
                select(
                    DocumentRequirement.legal_basis_id, func.bool_or(DocumentResource.is_searchable)
                )
                .join(DocumentResource, DocumentResource.requirement_id == DocumentRequirement.id)
                .where(DocumentRequirement.legal_basis_id.in_(ids))
                .group_by(DocumentRequirement.legal_basis_id)
            )
        }
        if ids and db.bind and db.bind.dialect.name == "postgresql"
        else {}
    )
    return [
        {
            "id": str(row.id),
            "norm_type": _enum(row.instrument_type),
            "number": row.reference,
            "date": row.effective_from,
            "title": row.title,
            "url": row.official_url,
            "located": bool(row.official_url),
            "searchable": resources.get(row.id),
            "source": ev[row.evidence_id],
            "observations": row.description,
            "limitations": []
            if row.official_url
            else ["La URL oficial de la norma no está disponible en los datos persistidos."],
        }
        for row in rows
    ]


def transparency(db: Session, institution: Institution) -> dict[str, Any]:
    assessments = list(
        db.scalars(
            select(TransparencyAssessment)
            .where(TransparencyAssessment.institution_id == institution.id)
            .order_by(
                TransparencyAssessment.assessment_date.desc(),
                TransparencyAssessment.coverage_percentage.desc(),
                TransparencyAssessment.methodology_version.desc(),
                TransparencyAssessment.id.desc(),
            )
        )
    )
    if not assessments:
        return {
            "latest_assessment": None,
            "historical_assessments": [],
            "ranking_enabled": False,
            "limitations": [PUBLIC_LIMITATION, "No hay evaluación de transparencia disponible."],
        }
    latest = assessments[0]
    components = list(
        db.execute(
            select(AssessmentComponent, TransparencyObservation)
            .join(
                TransparencyObservation,
                AssessmentComponent.observation_id == TransparencyObservation.id,
            )
            .where(AssessmentComponent.assessment_id == latest.id)
            .order_by(AssessmentComponent.dimension)
        )
    )
    ev = _evidence_map(db, {component.evidence_id for component, _ in components})
    public_components = []
    for component, observation in components:
        explanation = (
            component.public_explanation or "Resultado documental conforme a la regla indicada."
        )
        reason = explanation  # never expose the internal calculation_reason field
        public_components.append(
            {
                "dimension": component.dimension,
                "awarded_score": component.score,
                "maximum_score": component.maximum_score,
                "rule_code": component.rule_code,
                "public_explanation": explanation,
                "calculation_reason": reason,
                "evidence": ev[component.evidence_id],
                "observation_status": _enum(component.verification_status),
                "checked_at": observation.observed_at,
            }
        )
    limitations = [SCORE_LIMITATION, PUBLIC_LIMITATION]
    if latest.maturity_status != "complete":
        limitations.append(
            "La evaluación es parcial y mantiene dimensiones pendientes; "
            "no representa cobertura del 100 %."
        )
    item = {
        **_assessment_summary(latest),
        "raw_score": latest.score,
        "evaluated_max_score": latest.maximum_score,
        "rank": None,
        "comparison_position": None,
        "ranking_enabled": False,
        "components": public_components,
        "public_explanation": latest.classification_public,
        "limitations": limitations,
    }
    item.pop("normalized_score", None)
    item["normalized_score"] = latest.normalized_score
    item.pop("coverage_percentage", None)
    item["coverage_percentage"] = latest.coverage_percentage
    item.pop("maturity_status", None)
    item["maturity_status"] = latest.maturity_status
    return {
        "latest_assessment": item,
        "historical_assessments": [_assessment_summary(row) for row in assessments],
        "ranking_enabled": False,
        "limitations": limitations,
    }


def institution_detail(db: Session, institution: Institution) -> dict[str, Any]:
    rels = relationships(db, institution)
    trans = transparency(db, institution)
    links = list(
        db.execute(
            select(InstitutionEvidence.evidence_id).where(
                InstitutionEvidence.institution_id == institution.id
            )
        )
    )
    ev = _evidence_map(db, {row[0] for row in links})
    evidence = list(ev.values())
    return {
        "id": str(institution.id),
        "slug": institution.slug or str(institution.id),
        "official_name": institution.name,
        "short_name": institution.acronym,
        "institution_type": _enum(institution.institution_type or institution.kind),
        "status": _enum(institution.operational_status),
        "creation_date": institution.creation_date,
        "functions_summary": institution.functions_summary,
        "legal_basis_summary": legal_basis(db, institution),
        "official_website": institution.official_website,
        "current_authority": authority_for_institution(db, institution),
        "current_relationships": [r for r in rels if r["is_current"]],
        "official_sources": [e for e in evidence if e["official_source"]],
        "evidence": evidence,
        "latest_transparency_assessment": trans["latest_assessment"],
        "assessment_history": trans["historical_assessments"],
        "documentary_gaps": trans["limitations"]
        if trans["latest_assessment"]
        else ["No hay evaluación documental disponible."],
        "last_updated_at": institution.last_reviewed_at,
        "public_limitation": PUBLIC_LIMITATION,
    }


def list_authorities(
    db: Session,
    *,
    page: int,
    page_size: int,
    search: str | None,
    institution_slug: str | None,
    position_type: str | None,
    active_only: bool,
    sort_by: str,
    sort_order: str,
) -> dict[str, Any]:
    conditions = [
        Person.status == PersonStatus.CONFIRMED,
        Position.status == PositionStatus.CANONICAL,
        *_executive_scope(),
    ]
    if search:
        conditions.append(
            or_(
                Person.full_name.ilike(f"%{search.strip()}%"),
                Position.official_name.ilike(f"%{search.strip()}%"),
            )
        )
    if institution_slug:
        conditions.append(Institution.slug == institution_slug)
    if position_type:
        conditions.append(Position.position_type == position_type)
    if active_only:
        conditions.extend(
            [
                Appointment.status.in_(CURRENT_STATUSES),
                or_(Appointment.end_date.is_(None), Appointment.end_date >= date.today()),
            ]
        )
    base = (
        select(Appointment, Person, Position, Institution)
        .join(Person, Appointment.person_id == Person.id)
        .join(Position, Appointment.position_id == Position.id)
        .join(Institution, Appointment.institution_id == Institution.id)
        .where(*conditions)
    )
    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    columns = {
        "public_name": Person.full_name,
        "position": Position.official_name,
        "start_date": Appointment.start_date,
    }
    col = columns[sort_by]
    order = col.desc().nullslast() if sort_order == "desc" else col.asc().nullslast()
    rows = db.execute(
        base.order_by(order, Appointment.id).offset((page - 1) * page_size).limit(page_size)
    )
    items = [
        {
            "person_id": str(p.id),
            "appointment_id": str(a.id),
            "public_name": p.full_name,
            "position": pos.official_name,
            "institution": _ref(inst),
            "appointment_status": _enum(a.status),
            "start_date": a.start_date,
            "end_date": a.end_date,
            "appointment_act_status": "located" if _act_located(a) else "not_located",
            "verification_status": "verified" if a.evidence_id else "partially_verified",
        }
        for a, p, pos, inst in rows
    ]
    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": _pages(total, page_size),
    }


def authority_detail(db: Session, identifier: str) -> dict[str, Any] | None:
    try:
        ident = uuid.UUID(identifier)
    except ValueError:
        return None
    appointment = db.get(Appointment, ident)
    person_id = appointment.person_id if appointment else ident
    person = db.scalar(
        select(Person).where(Person.id == person_id, Person.status == PersonStatus.CONFIRMED)
    )
    if not person:
        return None
    rows = list(
        db.execute(
            select(Appointment, Position, Institution)
            .join(Position, Appointment.position_id == Position.id)
            .join(Institution, Appointment.institution_id == Institution.id)
            .where(
                Appointment.person_id == person.id,
                Position.status.in_((PositionStatus.CANONICAL, PositionStatus.INACTIVE)),
                *_executive_scope(),
            )
            .order_by(Appointment.start_date.desc().nullslast(), Appointment.id)
        )
    )
    appointments = [
        _appointment_public(db, appointment_row, person, position, institution)
        for appointment_row, position, institution in rows
    ]
    inst_rows = list({institution.id: institution for _, _, institution in rows}.values())
    evidence = [
        e
        for item in appointments
        for e in item["appointment_evidence"] + item["current_status_evidence"]
    ]
    return {
        "person_id": str(person.id),
        "public_name": person.full_name,
        "positions": sorted({item["position"] for item in appointments}),
        "appointments": appointments,
        "periods": [
            {"start_date": item["start_date"], "end_date": item["end_date"]}
            for item in appointments
        ],
        "evidence": evidence,
        "related_institutions": [_ref(row) for row in inst_rows],
        "limitations": [
            PUBLIC_LIMITATION,
            "Solo se publica la identidad y trayectoria institucional persistida en PE-04.",
        ],
    }


def changes(
    db: Session,
    *,
    date_from: date | None,
    date_to: date | None,
    change_type: str | None,
    institution_slug: str | None,
    page: int,
    page_size: int,
) -> dict[str, Any]:
    events: list[dict[str, Any]] = []
    inst_by_id = {row.id: row for row in db.scalars(select(Institution).where(*_executive_scope()))}

    def allowed(kind: str, inst_id: uuid.UUID | None, occurred: datetime) -> bool:
        inst = inst_by_id.get(inst_id) if inst_id else None
        return (
            (not change_type or kind == change_type)
            and (not institution_slug or bool(inst and inst.slug == institution_slug))
            and (not date_from or occurred.date() >= date_from)
            and (not date_to or occurred.date() <= date_to)
        )

    for appointment_row in db.scalars(
        select(Appointment).where(Appointment.institution_id.in_(inst_by_id))
    ):
        event_date = (
            appointment_row.end_date
            if appointment_row.status in (AppointmentStatus.ENDED, AppointmentStatus.REVOKED)
            else appointment_row.start_date
        )
        occurred = (
            datetime.combine(event_date, time.min, UTC)
            if event_date
            else appointment_row.created_at
        )
        kind = (
            "termination"
            if appointment_row.status in (AppointmentStatus.ENDED, AppointmentStatus.REVOKED)
            else "appointment"
        )
        if appointment_row.institution_id and allowed(
            kind, appointment_row.institution_id, occurred
        ):
            events.append(
                {
                    "id": str(appointment_row.id),
                    "change_type": kind,
                    "occurred_at": occurred,
                    "institution": _ref(inst_by_id[appointment_row.institution_id]),
                    "description": "Nombramiento o cambio de vigencia persistido.",
                    "evidence": [],
                }
            )
    relationship_rows = db.execute(
        select(InstitutionRelationship, Evidence, Source)
        .join(Evidence, InstitutionRelationship.evidence_id == Evidence.id)
        .join(Source, Evidence.source_id == Source.id)
        .where(
            or_(
                InstitutionRelationship.parent_institution_id.in_(inst_by_id),
                InstitutionRelationship.child_institution_id.in_(inst_by_id),
            )
        )
    )
    for relationship, evidence_row, source_row in relationship_rows:
        inst_id = (
            relationship.child_institution_id
            if relationship.child_institution_id in inst_by_id
            else relationship.parent_institution_id
        )
        occurred = relationship.created_at
        if allowed("new_relationship", inst_id, occurred):
            events.append(
                {
                    "id": str(relationship.id),
                    "change_type": "new_relationship",
                    "occurred_at": occurred,
                    "institution": _ref(inst_by_id[inst_id]),
                    "description": "Relación institucional persistida con evidencia.",
                    "evidence": [_evidence(evidence_row, source_row)],
                }
            )
    for assessment_row in db.scalars(
        select(TransparencyAssessment).where(TransparencyAssessment.institution_id.in_(inst_by_id))
    ):
        occurred = datetime.combine(assessment_row.assessment_date, time.min, UTC)
        if allowed("new_assessment", assessment_row.institution_id, occurred):
            events.append(
                {
                    "id": str(assessment_row.id),
                    "change_type": "new_assessment",
                    "occurred_at": occurred,
                    "institution": _ref(inst_by_id[assessment_row.institution_id]),
                    "description": (
                        "Evaluación publicada con metodología "
                        f"{assessment_row.methodology_version}."
                    ),
                    "evidence": [],
                }
            )
    for m in db.scalars(
        select(TransparencyMethodology).where(TransparencyMethodology.published_at.is_not(None))
    ):
        if m.published_at and allowed("methodology_change", None, m.published_at):
            events.append(
                {
                    "id": m.version,
                    "change_type": "methodology_change",
                    "occurred_at": m.published_at,
                    "institution": None,
                    "description": f"Metodología {m.version} publicada.",
                    "evidence": [],
                }
            )
    events.sort(key=lambda item: item["occurred_at"], reverse=True)
    total = len(events)
    items = events[(page - 1) * page_size : page * page_size]
    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": _pages(total, page_size),
    }
