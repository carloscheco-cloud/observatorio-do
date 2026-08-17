import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.actors import canonical_actor_type
from app.modules.evidence.models import Evidence
from app.modules.institutions.models import (
    Institution,
    InstitutionEvidence,
    InstitutionStatus,
)
from app.modules.institutions.schemas import InstitutionCreate
from app.modules.territories.models import Territory


class InvalidInstitution(ValueError):
    pass


def list_institutions(db: Session) -> list[Institution]:
    return list(db.scalars(select(Institution).order_by(Institution.name)))


def create_institution(
    db: Session, payload: InstitutionCreate, *, actor_type: str = "human"
) -> Institution:
    canonical_actor_type(actor_type)
    if db.get(Territory, payload.territory_id) is None:
        raise InvalidInstitution("Territory does not exist")
    if db.get(Evidence, payload.evidence_id) is None:
        raise InvalidInstitution("Evidence does not exist")

    institution = Institution(
        name=payload.name.strip(),
        kind=payload.kind.strip(),
        acronym=payload.acronym.strip().upper() if payload.acronym else None,
        slug=payload.slug,
        state_branch=payload.state_branch,
        institution_type=payload.institution_type,
        operational_status=payload.operational_status,
        coverage_level=payload.coverage_level,
        official_website=str(payload.official_website) if payload.official_website else None,
        functions_summary=payload.functions_summary,
        creation_date=payload.creation_date,
        last_reviewed_at=payload.last_reviewed_at,
        territory_id=payload.territory_id,
        status=InstitutionStatus.DRAFT,
    )
    institution.evidence_links.append(
        InstitutionEvidence(evidence_id=payload.evidence_id, relation="supports_existence")
    )
    db.add(institution)
    try:
        db.flush()
        institution.status = InstitutionStatus.CONFIRMED
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise InvalidInstitution("Institution name or slug already exists") from exc
    db.refresh(institution)
    return institution


def evidence_ids(db: Session, institution_id: uuid.UUID) -> list[uuid.UUID]:
    statement = select(InstitutionEvidence.evidence_id).where(
        InstitutionEvidence.institution_id == institution_id
    )
    return list(db.scalars(statement))
