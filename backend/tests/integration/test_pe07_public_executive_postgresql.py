from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.main import _requests, app
from app.modules.digital_transparency.loader import load as load_pe05
from app.modules.digital_transparency.models import ResourceCheck, SearchabilityCheck
from app.modules.digital_transparency.pe06b import load as load_pe06b
from app.modules.digital_transparency.pe06d import load as load_pe06d
from app.modules.executive_authorities.loader import load_authorities
from app.modules.executive_dependencies.loader import load_dependencies
from app.modules.executive_inventory.loader import load_inventory
from tests.integration.test_postgresql_guards import migrate

pytestmark = pytest.mark.integration
PRIVATE_MARKERS = (
    "raw_payload",
    "content_hash",
    "national_id_hash",
    "metadata_",
    "calculation_details",
    "reviewer_notes",
    "password",
    "traceback",
    "file://",
    "c:\\",
)


def _assert_public(payload: object) -> None:
    serialized = str(payload).casefold()
    assert all(marker not in serialized for marker in PRIVATE_MARKERS)


def test_pe07_contract_against_pe02_through_pe06d(postgres_url: str) -> None:
    migrate(postgres_url)
    engine = create_engine(postgres_url)
    with Session(engine) as db:
        load_inventory(db)
        load_dependencies(db)
        load_authorities(db)
        load_pe05(db)
        assert db.query(ResourceCheck).count() == 0
        assert db.query(SearchabilityCheck).count() == 0
        load_pe06b(db)
        assert db.query(ResourceCheck).count() == 16
        assert db.query(SearchabilityCheck).count() == 15
        load_pe06d(db)

        _requests.clear()
        previous_overrides = app.dependency_overrides.copy()
        app.dependency_overrides[get_db] = lambda: db
        try:
            with TestClient(app) as client:
                summary = client.get("/api/v1/executive/summary")

                listing = client.get("/api/v1/executive/institutions?page=1&page_size=5")
                searched = client.get(
                    "/api/v1/executive/institutions", params={"search": "Administración Pública"}
                )
                ministries = client.get(
                    "/api/v1/executive/institutions",
                    params={"institution_type": "ministry", "page_size": 100},
                )
                assessed = client.get(
                    "/api/v1/executive/institutions",
                    params={"has_transparency_assessment": True, "page_size": 100},
                )
                complete_filter = client.get(
                    "/api/v1/executive/institutions",
                    params={"maturity_status": "complete", "page_size": 100},
                )
                sorted_score = client.get(
                    "/api/v1/executive/institutions",
                    params={"sort_by": "transparency_score", "sort_order": "desc"},
                )
                invalid_zero = client.get("/api/v1/executive/institutions", params={"page_size": 0})
                invalid_large = client.get(
                    "/api/v1/executive/institutions", params={"page_size": 101}
                )
                invalid_sort = client.get(
                    "/api/v1/executive/institutions", params={"sort_by": "internal_column"}
                )

                profile = client.get(
                    "/api/v1/executive/institutions/ministerio-de-administracion-publica"
                )
                missing_profile = client.get("/api/v1/executive/institutions/inexistente")

                located_authority = client.get(
                    "/api/v1/executive/institutions/ministerio-de-administracion-publica/authority"
                )
                unlocated_authority = client.get(
                    "/api/v1/executive/institutions/ministerio-de-deportes-y-recreacion/authority"
                )

                incoming = client.get(
                    "/api/v1/executive/institutions/ministerio-de-administracion-publica/relationships",
                    params={"direction": "incoming"},
                )
                outgoing = client.get(
                    "/api/v1/executive/institutions/ministerio-de-administracion-publica/relationships",
                    params={"direction": "outgoing"},
                )
                all_relationships = client.get(
                    "/api/v1/executive/institutions/ministerio-de-administracion-publica/relationships",
                    params={"direction": "all"},
                )
                invalid_direction = client.get(
                    "/api/v1/executive/institutions/presidencia-de-la-republica/relationships",
                    params={"direction": "sideways"},
                )

                legal_basis = client.get(
                    "/api/v1/executive/institutions/presidencia-de-la-republica/legal-basis"
                )
                partial = client.get(
                    "/api/v1/executive/institutions/presidencia-de-la-republica/transparency"
                )
                complete = client.get(
                    "/api/v1/executive/institutions/ministerio-de-administracion-publica/transparency"
                )

                authorities = client.get("/api/v1/executive/authorities?page_size=100")
                authority_filter = client.get(
                    "/api/v1/executive/authorities",
                    params={"institution_slug": "presidencia-de-la-republica"},
                )
                authority_item = authority_filter.json()["items"][0]
                person_detail = client.get(
                    f"/api/v1/executive/authorities/{authority_item['person_id']}"
                )
                appointment_detail = client.get(
                    f"/api/v1/executive/authorities/{authority_item['appointment_id']}"
                )
                missing_authority = client.get(
                    "/api/v1/executive/authorities/00000000-0000-0000-0000-000000000000"
                )

                changes = client.get("/api/v1/executive/changes?page_size=100")
                assessment_changes = client.get(
                    "/api/v1/executive/changes",
                    params={
                        "date_from": "2026-08-04",
                        "date_to": "2026-08-04",
                        "change_type": "new_assessment",
                        "page_size": 100,
                    },
                )
                invalid_range = client.get(
                    "/api/v1/executive/changes?date_from=2026-08-05&date_to=2026-08-04"
                )
        finally:
            app.dependency_overrides.clear()
            app.dependency_overrides.update(previous_overrides)
            _requests.clear()

        summary_payload = summary.json()
        assert summary.status_code == 200
        assert summary_payload["total_institutions"] == 25
        assert summary_payload["total_active_institutions"] == 25
        assert summary_payload["total_ministries"] == 23
        assert summary_payload["presidency_present"] is True
        assert summary_payload["vice_presidency_present"] is True
        assert summary_payload["total_current_authorities"] == 25
        assert summary_payload["total_relationships"] > 0
        assert summary_payload["institutions_with_transparency_assessment"] == 25
        assert summary_payload["institutions_with_complete_assessment"] == 5
        assert summary_payload["institutions_with_partial_assessment"] == 20
        assert summary_payload["ranking_enabled"] is False

        assert listing.status_code == 200
        assert listing.json()["page_size"] == 5 and listing.json()["pages"] == 5
        assert searched.json()["total"] == 1
        assert ministries.json()["total"] == 23
        assert assessed.json()["total"] == 25
        assert complete_filter.json()["total"] == 5
        assert sorted_score.status_code == 200
        assert invalid_zero.status_code == 422
        assert invalid_large.status_code == 422
        assert invalid_sort.status_code == 422

        profile_payload = profile.json()
        assert profile.status_code == 200
        assert profile_payload["official_sources"]
        assert profile_payload["current_authority"]
        assert profile_payload["latest_transparency_assessment"]
        assert profile_payload["documentary_gaps"]
        assert profile_payload["public_limitation"]
        assert missing_profile.status_code == 404

        assert located_authority.status_code == 200
        assert located_authority.json()["act_located"] is True
        assert unlocated_authority.status_code == 200
        assert unlocated_authority.json()["act_located"] is False
        assert "no fue localizado" in " ".join(unlocated_authority.json()["limitations"])

        assert incoming.status_code == outgoing.status_code == all_relationships.status_code == 200
        assert incoming.json() == []
        assert outgoing.json()
        assert len(all_relationships.json()) == len(outgoing.json())
        assert all(item["direction"] == "incoming" for item in incoming.json())
        assert all(item["direction"] == "outgoing" for item in outgoing.json())
        assert invalid_direction.status_code == 422

        assert legal_basis.status_code == 200
        assert legal_basis.json()
        assert all(item["source"] and item["norm_type"] for item in legal_basis.json())

        partial_payload = partial.json()["latest_assessment"]
        complete_payload = complete.json()["latest_assessment"]
        assert Decimal(partial_payload["coverage_percentage"]) == Decimal("45")
        assert partial_payload["maturity_status"] == "partial"
        assert Decimal(complete_payload["coverage_percentage"]) == Decimal("100")
        assert complete_payload["maturity_status"] == "complete"
        assert complete_payload["rank"] is None
        assert complete_payload["comparison_position"] is None
        assert complete_payload["ranking_enabled"] is False
        assert len(complete_payload["components"]) == 8
        assert sum(bool(item["rule_code"]) for item in complete_payload["components"]) == 5
        assert all(
            "rule_code" in item and item["public_explanation"] and item["calculation_reason"]
            for item in complete_payload["components"]
        )

        assert authorities.status_code == 200 and authorities.json()["total"] == 25
        assert authority_filter.json()["total"] == 1
        assert person_detail.status_code == appointment_detail.status_code == 200
        assert person_detail.json()["person_id"] == appointment_detail.json()["person_id"]
        assert missing_authority.status_code == 404

        assert changes.status_code == 200 and changes.json()["items"]
        assert assessment_changes.status_code == 200
        assert assessment_changes.json()["items"]
        assert all(
            item["change_type"] == "new_assessment" for item in assessment_changes.json()["items"]
        )
        assert invalid_range.status_code == 400

        for response in (
            summary,
            listing,
            profile,
            located_authority,
            unlocated_authority,
            incoming,
            outgoing,
            legal_basis,
            partial,
            complete,
            authorities,
            person_detail,
            appointment_detail,
            changes,
        ):
            _assert_public(response.json())
            assert response.headers["etag"]
    engine.dispose()
