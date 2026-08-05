from datetime import date
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.public_api import executive_service as service
from app.modules.public_api.executive_schemas import (
    AuthorityDetail,
    AuthorityListItem,
    ChangeItem,
    ExecutiveSummary,
    InstitutionDetail,
    InstitutionListItem,
    LegalDocument,
    Page,
    PersonAuthorityDetail,
    RelationshipItem,
    TransparencyResponse,
)

router = APIRouter(prefix="/executive", tags=["Executive Public API"])
Db = Annotated[Session, Depends(get_db)]
PageNumber = Annotated[int, Query(ge=1)]
PageSize = Annotated[int, Query(ge=1, le=100)]


def _institution_or_404(db: Session, slug: str):  # type: ignore[no-untyped-def]
    institution = service._institution(db, slug)
    if institution is None:
        raise HTTPException(
            404,
            detail={
                "code": "institution_not_found",
                "message": "La institución no fue localizada en los datos públicos.",
            },
        )
    return institution


@router.get("/summary", response_model=ExecutiveSummary, summary="Resumen del Poder Ejecutivo")
def executive_summary(db: Db) -> ExecutiveSummary:
    return ExecutiveSummary.model_validate(service.summary(db))


@router.get("/institutions", response_model=Page[InstitutionListItem])
def executive_institutions(
    db: Db,
    page: PageNumber = 1,
    page_size: PageSize = 20,
    search: str | None = Query(None, min_length=1, max_length=120),
    institution_type: str | None = Query(None, max_length=80),
    parent_slug: str | None = Query(None, max_length=320),
    has_current_authority: bool | None = None,
    has_transparency_assessment: bool | None = None,
    maturity_status: Literal["partial", "complete"] | None = None,
    sort_by: Literal[
        "official_name",
        "institution_type",
        "updated_at",
        "transparency_score",
        "transparency_coverage",
    ] = "official_name",
    sort_order: Literal["asc", "desc"] = "asc",
) -> Page[InstitutionListItem]:
    return Page[InstitutionListItem].model_validate(
        service.list_institutions(
            db,
            page=page,
            page_size=page_size,
            search=search,
            institution_type=institution_type,
            parent_slug=parent_slug,
            has_current_authority=has_current_authority,
            has_transparency_assessment=has_transparency_assessment,
            maturity_status=maturity_status,
            sort_by=sort_by,
            sort_order=sort_order,
        )
    )


@router.get("/institutions/{slug}", response_model=InstitutionDetail)
def executive_institution(slug: str, db: Db) -> InstitutionDetail:
    return InstitutionDetail.model_validate(
        service.institution_detail(db, _institution_or_404(db, slug))
    )


@router.get("/institutions/{slug}/authority", response_model=AuthorityDetail)
def institution_authority(slug: str, db: Db) -> AuthorityDetail:
    institution = _institution_or_404(db, slug)
    result = service.authority_for_institution(db, institution)
    if result is None:
        raise HTTPException(
            404,
            detail={
                "code": "authority_not_found",
                "message": "No se localizó una autoridad actual confirmada para la institución.",
            },
        )
    return AuthorityDetail.model_validate(result)


@router.get("/institutions/{slug}/relationships", response_model=list[RelationshipItem])
def institution_relationships(
    slug: str, db: Db, direction: Literal["incoming", "outgoing", "all"] = "all"
) -> list[RelationshipItem]:
    return [
        RelationshipItem.model_validate(item)
        for item in service.relationships(db, _institution_or_404(db, slug), direction)
    ]


@router.get("/institutions/{slug}/legal-basis", response_model=list[LegalDocument])
def institution_legal_basis(slug: str, db: Db) -> list[LegalDocument]:
    return [
        LegalDocument.model_validate(item)
        for item in service.legal_basis(db, _institution_or_404(db, slug))
    ]


@router.get("/institutions/{slug}/transparency", response_model=TransparencyResponse)
def institution_transparency(slug: str, db: Db) -> TransparencyResponse:
    return TransparencyResponse.model_validate(
        service.transparency(db, _institution_or_404(db, slug))
    )


@router.get("/authorities", response_model=Page[AuthorityListItem])
def executive_authorities(
    db: Db,
    page: PageNumber = 1,
    page_size: PageSize = 20,
    search: str | None = Query(None, min_length=1, max_length=120),
    institution_slug: str | None = Query(None, max_length=320),
    position_type: str | None = Query(None, max_length=100),
    active_only: bool = True,
    sort_by: Literal["public_name", "position", "start_date"] = "public_name",
    sort_order: Literal["asc", "desc"] = "asc",
) -> Page[AuthorityListItem]:
    return Page[AuthorityListItem].model_validate(
        service.list_authorities(
            db,
            page=page,
            page_size=page_size,
            search=search,
            institution_slug=institution_slug,
            position_type=position_type,
            active_only=active_only,
            sort_by=sort_by,
            sort_order=sort_order,
        )
    )


@router.get("/authorities/{person_or_appointment_id}", response_model=PersonAuthorityDetail)
def executive_authority(person_or_appointment_id: str, db: Db) -> PersonAuthorityDetail:
    result = service.authority_detail(db, person_or_appointment_id)
    if result is None:
        raise HTTPException(
            404,
            detail={
                "code": "authority_not_found",
                "message": "La autoridad no fue localizada en los datos públicos.",
            },
        )
    return PersonAuthorityDetail.model_validate(result)


@router.get("/changes", response_model=Page[ChangeItem])
def executive_changes(
    db: Db,
    date_from: date | None = None,
    date_to: date | None = None,
    change_type: Literal[
        "new_institution",
        "status_change",
        "new_relationship",
        "appointment",
        "termination",
        "new_assessment",
        "methodology_change",
    ]
    | None = None,
    institution_slug: str | None = Query(None, max_length=320),
    page: PageNumber = 1,
    page_size: PageSize = 20,
) -> Page[ChangeItem]:
    if date_from and date_to and date_from > date_to:
        raise HTTPException(
            400,
            detail={
                "code": "invalid_date_range",
                "message": "La fecha inicial debe ser anterior o igual a la fecha final.",
            },
        )
    return Page[ChangeItem].model_validate(
        service.changes(
            db,
            date_from=date_from,
            date_to=date_to,
            change_type=change_type,
            institution_slug=institution_slug,
            page=page,
            page_size=page_size,
        )
    )
