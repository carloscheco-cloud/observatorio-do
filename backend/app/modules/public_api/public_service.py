import math
import unicodedata
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.institutions.models import Institution, InstitutionStatus
from app.modules.persons.models import Person
from app.modules.positions.models import Position
from app.modules.risk_engine.models import RiskFinding, RiskType
from app.modules.territories.models import Territory

NEVER_PUBLIC = frozenset(
    {
        "raw_payload",
        "reviewer_notes",
        "internal_explanation",
        "internal_message_template",
        "metadata_",
        "national_id_hash",
        "tax_id_hash",
        "registration_hash",
        "vin_hash",
        "serial_hash",
        "policy_hash",
    }
)


def now() -> datetime:
    return datetime.now(UTC)


def normalize_query(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).strip()
    return " ".join(normalized.split())


def pagination(page: int, page_size: int, total: int) -> dict[str, Any]:
    pages = math.ceil(total / page_size) if total else 0
    return {
        "page": page,
        "page_size": page_size,
        "total_items": total,
        "total_pages": pages,
        "has_next": page < pages,
        "has_previous": page > 1,
    }


def collection(
    data: list[dict[str, Any]],
    page: int,
    page_size: int,
    total: int,
    filters: dict[str, Any] | None = None,
    sort: str = "name",
    warnings: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "data": data,
        "pagination": pagination(page, page_size, total),
        "filters_applied": filters or {},
        "sort": sort,
        "generated_at": now(),
        "source_freshness": "unknown",
        "warnings": warnings or [],
    }


def empty(page: int, page_size: int, domain: str) -> dict[str, Any]:
    return collection(
        [], page, page_size, 0, warnings=[f"No hay datos públicos disponibles para {domain}."]
    )


def institution_dict(row: Institution) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "name": row.name,
        "kind": row.kind,
        "territory_id": str(row.territory_id),
        "status": str(row.status.value),
    }


def list_institutions(
    db: Session, page: int, page_size: int, q: str | None, sort: str
) -> dict[str, Any]:
    query = select(Institution).where(Institution.status == InstitutionStatus.CONFIRMED)
    count = (
        select(func.count())
        .select_from(Institution)
        .where(Institution.status == InstitutionStatus.CONFIRMED)
    )
    filters: dict[str, Any] = {}
    if q:
        term = normalize_query(q)
        query = query.where(Institution.name.ilike(f"%{term}%"))
        count = count.where(Institution.name.ilike(f"%{term}%"))
        filters["q"] = term
    order = Institution.name.desc() if sort == "-name" else Institution.name.asc()
    total = db.scalar(count) or 0
    rows = db.scalars(query.order_by(order).offset((page - 1) * page_size).limit(page_size))
    return collection(
        [institution_dict(row) for row in rows], page, page_size, total, filters, sort
    )


def get_institution(db: Session, institution_id: uuid.UUID) -> dict[str, Any] | None:
    row = db.scalar(
        select(Institution).where(
            Institution.id == institution_id,
            Institution.status == InstitutionStatus.CONFIRMED,
        )
    )
    return institution_dict(row) if row else None


def public_findings(
    db: Session, page: int, page_size: int, institution_id: uuid.UUID | None = None
) -> dict[str, Any]:
    conditions = [RiskFinding.visibility == "public", RiskFinding.status == "published"]
    if institution_id:
        conditions.append(RiskFinding.institution_id == institution_id)
    query = select(RiskFinding).where(*conditions)
    total = db.scalar(select(func.count()).select_from(RiskFinding).where(*conditions)) or 0
    rows = db.scalars(
        query.order_by(RiskFinding.last_detected_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    data = [
        {
            "id": str(row.id),
            "code": row.finding_code,
            "domain": row.domain,
            "entity_type": row.entity_type,
            "entity_id": str(row.entity_id),
            "institution_id": str(row.institution_id) if row.institution_id else None,
            "title": row.title,
            "explanation": row.public_explanation,
            "severity": row.severity,
            "period_start": row.period_start,
            "period_end": row.period_end,
            "last_detected_at": row.last_detected_at,
        }
        for row in rows
    ]
    return collection(data, page, page_size, total, sort="-last_detected_at")


def search(
    db: Session, q: str, page: int, page_size: int, entity_type: str | None
) -> dict[str, Any]:
    term = normalize_query(q)
    pattern = f"%{term}%"
    results: list[dict[str, Any]] = []
    if entity_type in (None, "institution"):
        institution_rows = db.scalars(
            select(Institution)
            .where(
                Institution.status == InstitutionStatus.CONFIRMED,
                Institution.name.ilike(pattern),
            )
            .order_by(Institution.name)
            .limit(page_size + 1)
        )
        results.extend(
            {
                "id": str(row.id),
                "entity_type": "institution",
                "title": row.name,
                "subtitle": row.kind,
                "url": f"/instituciones/{row.id}",
                "score": 1.0 if row.name.casefold() == term.casefold() else 0.7,
            }
            for row in institution_rows
        )
    if entity_type in (None, "territory"):
        territory_rows = db.scalars(
            select(Territory)
            .where(Territory.name.ilike(pattern))
            .order_by(Territory.name)
            .limit(20)
        )
        results.extend(
            {
                "id": str(row.id),
                "entity_type": "territory",
                "title": row.name,
                "subtitle": row.type.value,
                "url": f"/territorios/{row.id}",
                "score": 0.65,
            }
            for row in territory_rows
        )
    results.sort(key=lambda item: (-float(item["score"]), str(item["title"])))
    start = (page - 1) * page_size
    return collection(
        results[start : start + page_size],
        page,
        page_size,
        len(results),
        {"q": term, **({"entity_type": entity_type} if entity_type else {})},
        "-score",
    )


def counts(db: Session) -> dict[str, int]:
    return {
        "institutions": db.scalar(
            select(func.count())
            .select_from(Institution)
            .where(Institution.status == InstitutionStatus.CONFIRMED)
        )
        or 0,
        "territories": db.scalar(select(func.count()).select_from(Territory)) or 0,
        "people": db.scalar(select(func.count()).select_from(Person)) or 0,
        "positions": db.scalar(select(func.count()).select_from(Position)) or 0,
        "public_findings": db.scalar(
            select(func.count())
            .select_from(RiskFinding)
            .where(RiskFinding.visibility == "public", RiskFinding.status == "published")
        )
        or 0,
    }


def taxonomy(db: Session, page: int, page_size: int) -> dict[str, Any]:
    query = select(RiskType).where(RiskType.status == "active")
    total = (
        db.scalar(select(func.count()).select_from(RiskType).where(RiskType.status == "active"))
        or 0
    )
    rows = db.scalars(
        query.order_by(RiskType.official_name).offset((page - 1) * page_size).limit(page_size)
    )
    data = [
        {
            "id": str(row.id),
            "code": row.stable_code,
            "name": row.official_name,
            "description": row.description,
            "domain": row.domain,
            "category": row.category,
            "default_severity": row.default_severity,
        }
        for row in rows
    ]
    return collection(data, page, page_size, total)
