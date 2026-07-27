import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.main import app
from app.modules.institutions.models import Institution, InstitutionStatus
from app.modules.public_api.public_service import NEVER_PUBLIC
from app.modules.territories.models import Territory, TerritoryType


def client_for(db: Session) -> TestClient:
    app.dependency_overrides[get_db] = lambda: db
    return TestClient(app)


def test_public_institutions_are_confirmed_paginated_and_private(db: Session) -> None:
    territory = Territory(
        name="Territorio ficticio bloque 12",
        code="T-FICT-12",
        type=TerritoryType.MUNICIPALITY,
    )
    db.add(territory)
    db.flush()
    confirmed = Institution(
        name="Ayuntamiento Ficticio de Transparencia",
        kind="municipality",
        territory_id=territory.id,
        status=InstitutionStatus.CONFIRMED,
    )
    draft = Institution(
        name="Institución no revisada",
        kind="agency",
        territory_id=territory.id,
        status=InstitutionStatus.DRAFT,
    )
    db.add_all([confirmed, draft])
    db.commit()

    with client_for(db) as client:
        response = client.get("/api/v1/public/institutions?page=1&page_size=10")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["pagination"]["total_items"] == 1
    assert payload["data"][0]["name"] == confirmed.name
    serialized = str(payload).casefold()
    assert draft.name.casefold() not in serialized
    assert all(field.casefold() not in serialized for field in NEVER_PUBLIC)
    assert response.headers["cache-control"].startswith("public")
    assert response.headers["etag"]


def test_search_validation_and_empty_state(db: Session) -> None:
    with client_for(db) as client:
        invalid = client.get("/api/v1/public/search?q=x")
        empty = client.get("/api/v1/public/search?q=inexistente")
    app.dependency_overrides.clear()

    assert invalid.status_code == 422
    assert invalid.json()["code"] == "validation_error"
    assert empty.status_code == 200
    assert empty.json()["data"] == []


def test_public_surface_has_expected_routes() -> None:
    paths = set(app.openapi()["paths"])
    expected = {
        "/api/v1/public/institutions",
        "/api/v1/public/search",
        "/api/v1/public/compare",
        "/api/v1/public/export",
        "/api/v1/public/findings",
        "/api/v1/public/payroll/summary",
        "/api/v1/public/budget/execution",
        "/api/v1/public/procurement/processes",
        "/api/v1/public/debt/instruments",
        "/api/v1/public/assets",
        "/api/v1/public/data-freshness",
        "/api/v1/public/status",
    }
    assert expected <= paths
    assert "/api/v1/public/internal/source-catalog" not in paths


def test_missing_or_non_public_resource_is_not_disclosed(db: Session) -> None:
    with client_for(db) as client:
        response = client.get(f"/api/v1/public/institutions/{uuid.uuid4()}")
    app.dependency_overrides.clear()
    assert response.status_code == 404
    assert "traceback" not in response.text.casefold()
