import csv
import io
import json
import uuid
from datetime import date
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.public_api import public_service as service

router = APIRouter(prefix="/public")
Db = Annotated[Session, Depends(get_db)]
Page = Annotated[int, Query(ge=1)]
PageSize = Annotated[int, Query(ge=1, le=100)]


def not_found(resource: str) -> HTTPException:
    return HTTPException(
        status_code=404,
        detail={"code": "not_found", "message": f"{resource} no existe o no es público."},
    )


@router.get("/institutions", tags=["Institutions"], summary="Lista instituciones confirmadas")
def institutions(
    db: Db,
    page: Page = 1,
    page_size: PageSize = 20,
    q: str | None = Query(None, max_length=120),
    sort: Literal["name", "-name"] = "name",
) -> dict[str, Any]:
    return service.list_institutions(db, page, page_size, q, sort)


@router.get("/institutions/{institution_id}", tags=["Institutions"])
def institution(institution_id: uuid.UUID, db: Db) -> dict[str, Any]:
    data = service.get_institution(db, institution_id)
    if data is None:
        raise not_found("La institución")
    return {
        "data": data,
        "generated_at": service.now(),
        "source_freshness": "unknown",
        "traceability": {"evidence": "available_on_sources_endpoint"},
        "warnings": [],
    }


@router.get("/institutions/{institution_id}/profile", tags=["Institutions"])
def institution_profile(institution_id: uuid.UUID, db: Db) -> dict[str, Any]:
    data = service.get_institution(db, institution_id)
    if data is None:
        raise not_found("La institución")
    return {
        "data": {
            **data,
            "legal_basis": None,
            "parent_institution": None,
            "metrics": {},
            "coverage": {
                domain: "not_available"
                for domain in ("employment", "payroll", "budget", "procurement", "debt", "assets")
            },
            "data_quality": "under_review",
            "last_updated": None,
        },
        "generated_at": service.now(),
        "source_freshness": "unknown",
        "traceability": {"summary": "Consulte las fuentes públicas enlazadas."},
        "warnings": ["La ausencia de un valor no representa cero."],
    }


@router.get("/institutions/{institution_id}/findings", tags=["Findings"])
def institution_findings(
    institution_id: uuid.UUID, db: Db, page: Page = 1, page_size: PageSize = 20
) -> dict[str, Any]:
    return service.public_findings(db, page, page_size, institution_id)


INSTITUTION_SECTIONS = (
    "history",
    "structure",
    "positions",
    "employment",
    "payroll",
    "budget",
    "procurement",
    "debt",
    "assets",
    "sources",
)


@router.get("/institutions/{institution_id}/{section}", tags=["Institutions"])
def institution_section(
    institution_id: uuid.UUID,
    section: Literal[
        "history",
        "structure",
        "positions",
        "employment",
        "payroll",
        "budget",
        "procurement",
        "debt",
        "assets",
        "sources",
    ],
    db: Db,
    page: Page = 1,
    page_size: PageSize = 20,
) -> dict[str, Any]:
    if service.get_institution(db, institution_id) is None:
        raise not_found("La institución")
    return service.empty(page, page_size, section)


@router.get("/search", tags=["Search"])
def search(
    db: Db,
    q: str = Query(min_length=2, max_length=120),
    entity_type: str | None = Query(None, pattern=r"^[a-z_]+$"),
    institution_id: uuid.UUID | None = None,
    territory_id: uuid.UUID | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    page: Page = 1,
    page_size: PageSize = 20,
    sort: Literal["-score", "title"] = "-score",
) -> dict[str, Any]:
    if date_from and date_to and date_from > date_to:
        raise HTTPException(
            422,
            detail={
                "code": "invalid_date_range",
                "message": "date_from debe ser anterior a date_to",
            },
        )
    result = service.search(db, q, page, page_size, entity_type)
    result["filters_applied"].update(
        {
            k: str(v)
            for k, v in {
                "institution_id": institution_id,
                "territory_id": territory_id,
                "date_from": date_from,
                "date_to": date_to,
            }.items()
            if v is not None
        }
    )
    result["sort"] = sort
    return result


@router.get("/findings", tags=["Findings"])
def findings(db: Db, page: Page = 1, page_size: PageSize = 20) -> dict[str, Any]:
    return service.public_findings(db, page, page_size)


@router.get("/findings/{finding_id}", tags=["Findings"])
def finding(finding_id: uuid.UUID, db: Db) -> dict[str, Any]:
    result = service.public_findings(db, 1, 100)
    item = next((row for row in result["data"] if row["id"] == str(finding_id)), None)
    if item is None:
        raise not_found("La alerta")
    return {
        "data": item,
        "generated_at": service.now(),
        "source_freshness": "unknown",
        "traceability": {},
        "warnings": ["Una señal observable no equivale a una acusación."],
    }


@router.get("/risk-summary", tags=["Findings"])
@router.get("/metrics", tags=["Sources"])
def metrics(db: Db) -> dict[str, Any]:
    return {
        "data": service.counts(db),
        "generated_at": service.now(),
        "period": None,
        "warnings": [
            "Los totales pertenecen a la cobertura disponible y no deben sumarse "
            "entre períodos incompatibles."
        ],
    }


@router.get("/risk-taxonomy", tags=["Findings"])
def risk_taxonomy(db: Db, page: Page = 1, page_size: PageSize = 20) -> dict[str, Any]:
    return service.taxonomy(db, page, page_size)


@router.get("/compare", tags=["Compare"])
def compare(
    entity_ids: Annotated[list[uuid.UUID], Query(min_length=1, max_length=5)],
    metrics: Annotated[list[str], Query(min_length=1, max_length=10)],
    entity_type: str = Query(pattern=r"^[a-z_]+$"),
    period_start: date | None = None,
    period_end: date | None = None,
) -> dict[str, Any]:
    return {
        "data": [
            {"entity_id": str(item), "metrics": {metric: None for metric in metrics}}
            for item in entity_ids
        ],
        "entity_type": entity_type,
        "period": {"start": period_start, "end": period_end},
        "generated_at": service.now(),
        "methodology": "Sólo se comparan unidades, monedas y períodos compatibles.",
        "warnings": ["No hay métricas comparables disponibles."],
    }


@router.get("/export", tags=["Exports"])
def export(
    db: Db,
    resource: Literal["institutions", "findings"],
    format: Literal["csv", "json"] = "csv",
    q: str | None = Query(None, max_length=120),
    limit: int = Query(1000, ge=1, le=5000),
) -> Response:
    payload = (
        service.list_institutions(db, 1, min(limit, 100), q, "name")
        if resource == "institutions"
        else service.public_findings(db, 1, min(limit, 100))
    )
    rows = payload["data"]
    if format == "json":
        return Response(
            json.dumps(
                {
                    "generated_at": service.now().isoformat(),
                    "license": "Consulte términos de uso",
                    "data": rows,
                },
                default=str,
            ),
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="{resource}.json"'},
        )
    output = io.StringIO()
    fields = list(rows[0]) if rows else ["message"]
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    if rows:
        for row in rows:
            writer.writerow({key: _csv_safe(value) for key, value in row.items()})
    else:
        writer.writerow({"message": "No hay datos públicos para los filtros seleccionados."})
    return Response(
        output.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{resource}.csv"',
            "X-Generated-At": service.now().isoformat(),
        },
    )


def _csv_safe(value: object) -> object:
    if isinstance(value, str) and value.startswith(("=", "+", "-", "@")):
        return f"'{value}"
    return value


@router.get("/status", tags=["Sources"])
def status(db: Db) -> dict[str, Any]:
    return {
        "availability": "available",
        "generated_at": service.now(),
        "coverage": service.counts(db),
        "delayed_sources": [],
        "warnings": [],
    }


@router.get("/methodology", tags=["Sources"])
def methodology() -> dict[str, Any]:
    return {
        "data": {
            "principles": ["trazabilidad", "privacidad", "revisión humana", "no acusación"],
            "coverage_states": ["complete", "partial", "not_available", "stale", "under_review"],
            "notice": (
                "Las señales son hechos observables para revisión y no equivalen a acusaciones."
            ),
        },
        "generated_at": service.now(),
    }


@router.get("/data-freshness", tags=["Sources"])
def freshness() -> dict[str, Any]:
    return {
        "data": [],
        "generated_at": service.now(),
        "warnings": ["No hay fuentes con frescura pública calculada."],
    }


COLLECTION_PATHS = {
    "persons": "People",
    "positions": "People",
    "appointments": "People",
    "territories": "Territories",
    "payroll/summary": "Payroll",
    "payroll/evolution": "Payroll",
    "payroll/comparison": "Payroll",
    "payroll/records": "Payroll",
    "budget/summary": "Budget",
    "budget/execution": "Budget",
    "budget/evolution": "Budget",
    "budget/comparison": "Budget",
    "budget/programs": "Budget",
    "procurement/processes": "Procurement",
    "procurement/contracts": "Procurement",
    "procurement/suppliers": "Procurement",
    "procurement/metrics": "Procurement",
    "debt/summary": "Debt",
    "debt/instruments": "Debt",
    "debt/service": "Debt",
    "debt/evolution": "Debt",
    "assets": "Assets",
    "assets/summary": "Assets",
    "assets/evolution": "Assets",
    "sources": "Sources",
}


def _make_collection(domain: str) -> Any:
    def endpoint(page: Page = 1, page_size: PageSize = 20) -> dict[str, Any]:
        return service.empty(page, page_size, domain)

    return endpoint


for _path, _tag in COLLECTION_PATHS.items():
    router.add_api_route(
        f"/{_path}",
        _make_collection(_path),
        methods=["GET"],
        tags=[_tag],
        name=f"public_{_path.replace('/', '_')}",
    )


DETAIL_PATHS = {
    "persons/{item_id}": "People",
    "persons/{item_id}/public-history": "People",
    "positions/{item_id}": "People",
    "territories/{item_id}": "Territories",
    "territories/{item_id}/institutions": "Territories",
    "territories/{item_id}/metrics": "Territories",
    "territories/{item_id}/findings": "Territories",
    "procurement/processes/{item_id}": "Procurement",
    "procurement/contracts/{item_id}": "Procurement",
    "procurement/suppliers/{item_id}": "Procurement",
    "debt/instruments/{item_id}": "Debt",
    "assets/{item_id}": "Assets",
    "sources/{item_id}": "Sources",
}


def _make_detail(domain: str) -> Any:
    def endpoint(item_id: uuid.UUID) -> dict[str, Any]:
        raise not_found(domain)

    return endpoint


for _path, _tag in DETAIL_PATHS.items():
    router.add_api_route(
        f"/{_path}",
        _make_detail(_path),
        methods=["GET"],
        tags=[_tag],
        name=f"public_{_path.replace('/', '_').replace('{item_id}', 'detail')}",
    )
