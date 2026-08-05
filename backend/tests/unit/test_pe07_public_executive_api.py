from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.main import app
from app.modules.institutions.models import (
    Institution,
    InstitutionStatus,
    InstitutionType,
    OperationalStatus,
    StateBranch,
)
from app.modules.territories.models import Territory, TerritoryType


def client_for(db: Session) -> TestClient:
    app.dependency_overrides[get_db] = lambda: db
    return TestClient(app)


def seed_executive(db: Session) -> tuple[Institution, Institution]:
    territory = Territory(name="República de prueba PE-07", code="PE07", type=TerritoryType.COUNTRY)
    db.add(territory)
    db.flush()
    ministry = Institution(
        name="Ministerio Público de Prueba",
        acronym="MPP",
        slug="ministerio-publico-prueba",
        kind="ministry",
        state_branch=StateBranch.EXECUTIVE,
        institution_type=InstitutionType.MINISTRY,
        operational_status=OperationalStatus.ACTIVE,
        territory_id=territory.id,
        status=InstitutionStatus.CONFIRMED,
    )
    hidden = Institution(
        name="Borrador no público",
        slug="borrador-no-publico",
        kind="ministry",
        state_branch=StateBranch.EXECUTIVE,
        institution_type=InstitutionType.MINISTRY,
        operational_status=OperationalStatus.ACTIVE,
        territory_id=territory.id,
        status=InstitutionStatus.DRAFT,
    )
    db.add_all([ministry, hidden])
    db.commit()
    return ministry, hidden


def test_summary_is_public_scoped_and_ranking_is_disabled(db: Session) -> None:
    seed_executive(db)
    with client_for(db) as client:
        response = client.get("/api/v1/executive/summary")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    payload = response.json()
    assert payload["total_institutions"] == 1
    assert payload["total_ministries"] == 1
    assert payload["ranking_enabled"] is False
    assert "corrupción" in " ".join(payload["limitations"])


def test_institution_list_search_pagination_and_safe_sort(db: Session) -> None:
    ministry, hidden = seed_executive(db)
    with client_for(db) as client:
        response = client.get(
            "/api/v1/executive/institutions",
            params={"search": "Público", "page_size": 1, "sort_by": "official_name"},
        )
        unsafe = client.get(
            "/api/v1/executive/institutions", params={"sort_by": "status;drop table"}
        )
        oversized = client.get("/api/v1/executive/institutions", params={"page_size": 101})
    app.dependency_overrides.clear()
    payload = response.json()
    assert response.status_code == 200
    assert payload == {
        **payload,
        "page": 1,
        "page_size": 1,
        "total": 1,
        "pages": 1,
    }
    assert payload["items"][0]["id"] == str(ministry.id)
    assert hidden.name not in response.text
    assert unsafe.status_code == 422
    assert oversized.status_code == 422


def test_detail_404_date_error_and_get_only_surface(db: Session) -> None:
    ministry, _ = seed_executive(db)
    with client_for(db) as client:
        detail = client.get(f"/api/v1/executive/institutions/{ministry.slug}")
        missing = client.get("/api/v1/executive/institutions/no-existe")
        invalid_dates = client.get(
            "/api/v1/executive/changes?date_from=2026-02-02&date_to=2026-01-01"
        )
        write = client.post("/api/v1/executive/institutions", json={})
    app.dependency_overrides.clear()
    assert detail.status_code == 200
    assert detail.json()["latest_transparency_assessment"] is None
    assert missing.status_code == 404
    assert invalid_dates.status_code == 400
    assert write.status_code == 405
    serialized = detail.text.casefold()
    for private in ("metadata", "notes", "content_hash", "national_id_hash", "raw_payload"):
        assert private not in serialized


def test_openapi_has_explicit_executive_contracts() -> None:
    paths = app.openapi()["paths"]
    expected = {
        "/api/v1/executive/summary",
        "/api/v1/executive/institutions",
        "/api/v1/executive/institutions/{slug}",
        "/api/v1/executive/institutions/{slug}/authority",
        "/api/v1/executive/institutions/{slug}/relationships",
        "/api/v1/executive/institutions/{slug}/legal-basis",
        "/api/v1/executive/institutions/{slug}/transparency",
        "/api/v1/executive/authorities",
        "/api/v1/executive/authorities/{person_or_appointment_id}",
        "/api/v1/executive/changes",
    }
    assert expected <= set(paths)
    assert all(set(paths[path]) <= {"get", "parameters"} for path in expected)
