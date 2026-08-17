from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.autonomy.mission import status_payload
from app.modules.institutions.models import Institution, InstitutionStatus, StateBranch

router = APIRouter(prefix="/public/state", tags=["State coverage"])
Db = Annotated[Session, Depends(get_db)]


@router.get("/institutions")
def branch_institutions(
    db: Db,
    branch: StateBranch,
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=250),
) -> dict[str, Any]:
    base = select(Institution).where(
        Institution.status == InstitutionStatus.CONFIRMED,
        Institution.state_branch == branch,
    )
    total = (
        db.scalar(
            select(func.count())
            .select_from(Institution)
            .where(
                Institution.status == InstitutionStatus.CONFIRMED,
                Institution.state_branch == branch,
            )
        )
        or 0
    )
    rows = list(
        db.scalars(base.order_by(Institution.name).offset((page - 1) * page_size).limit(page_size))
    )
    return {
        "data": [
            {
                "id": str(row.id),
                "name": row.name,
                "kind": row.kind,
                "acronym": row.acronym,
                "slug": row.slug,
                "state_branch": row.state_branch.value if row.state_branch else None,
                "institution_type": row.institution_type.value if row.institution_type else None,
                "operational_status": row.operational_status.value,
                "coverage_level": row.coverage_level.value,
                "official_website": row.official_website,
            }
            for row in rows
        ],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_items": total,
        },
        "filters_applied": {"branch": branch.value},
        "warnings": ["La cobertura publicada mejora de forma iterativa."],
    }


@router.get("/coverage")
def state_coverage(db: Db) -> dict[str, Any]:
    return status_payload(db)
