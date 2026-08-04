from datetime import date

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.appointments.models import Appointment
from app.modules.executive_authorities.loader import (
    InvalidManifest,
    load_authorities,
    read_manifest,
    rollback_authorities,
    validate_manifest,
)
from app.modules.executive_inventory.loader import load_inventory
from app.modules.persons.models import Person
from app.modules.positions.models import Position


def test_manifest_has_complete_separated_inventory() -> None:
    data = read_manifest()
    assert len(data["persons"]) == 25
    assert len(data["positions"]) == 25
    assert len(data["appointments"]) == 25
    assert len({item["slug"] for item in data["positions"]}) == 25
    assert {item["person"] for item in data["person_evidence"]} == {
        item["key"] for item in data["persons"]
    }
    assert not any(
        forbidden in item
        for item in data["persons"]
        for forbidden in ("national_id_hash", "birth_date", "address", "phone", "email", "party")
    )


def test_invalid_period_and_missing_evidence_are_rejected() -> None:
    data = read_manifest()
    data["appointments"][0]["end_date"] = "2024-08-15"
    with pytest.raises(InvalidManifest, match="precedes"):
        validate_manifest(data)
    data = read_manifest()
    data["appointment_evidence"] = data["appointment_evidence"][:-2]
    with pytest.raises(InvalidManifest, match="cover every"):
        validate_manifest(data)


def test_unidentified_act_keeps_active_status_and_null_decree() -> None:
    data = read_manifest()
    appointment = next(item for item in data["appointments"] if item["key"] == "minister-sports")
    assert appointment["status"] == "active"
    assert appointment["legal_act"] is None
    assert appointment["decree_number"] is None
    assert appointment["notes"]
    assert "juramentación" in appointment["start_date_basis"]


def test_decree_number_without_official_traceability_is_rejected() -> None:
    data = read_manifest()
    appointment = next(item for item in data["appointments"] if item["key"] == "minister-sports")
    appointment["decree_number"] = "999-99"
    with pytest.raises(InvalidManifest, match="official act traceability"):
        validate_manifest(data)


def test_appointment_and_current_status_evidence_are_distinct() -> None:
    data = read_manifest()
    for appointment in data["appointments"]:
        evidence = [
            item
            for item in data["appointment_evidence"]
            if item["appointment"] == appointment["key"]
        ]
        assert {item["relation"] for item in evidence} == {
            "supports_appointment",
            "supports_current_status",
        }
    tourism = [
        item for item in data["appointment_evidence"] if item["appointment"] == "minister-tourism"
    ]
    assert (
        next(item for item in tourism if item["relation"] == "supports_appointment")["source"]
        == "d324"
    )
    assert (
        next(item for item in tourism if item["relation"] == "supports_current_status")["source"]
        == "tourism"
    )


def test_announcement_is_not_used_as_start_date() -> None:
    data = read_manifest()
    housing = next(item for item in data["appointments"] if item["key"] == "minister-housing")
    mapre = next(item for item in data["appointments"] if item["key"] == "minister-mapre")
    assert housing["start_date"] == "2026-01-15"
    assert "efectos expresamente" in housing["start_date_basis"]
    assert mapre["start_date"] == "2024-07-17"


def test_null_start_date_requires_explanation() -> None:
    data = read_manifest()
    appointment = data["appointments"][0]
    appointment["start_date"] = None
    appointment["start_date_note"] = "Fecha jurídica no localizada."
    validate_manifest(data)


def test_dry_run_idempotence_and_rollback_preserve_pe02(db: Session) -> None:
    load_inventory(db)
    institution_count = db.scalar(select(func.count()).select_from(Position)) or 0
    preview = load_authorities(db, dry_run=True)
    assert preview.created == 75
    assert db.scalar(select(func.count()).select_from(Person)) == 0
    first = load_authorities(db)
    second = load_authorities(db)
    assert first.created == 75
    assert second.unchanged == 75
    assert db.scalar(select(func.count()).select_from(Person)) == 25
    assert db.scalar(select(func.count()).select_from(Position)) == institution_count + 25
    assert db.scalar(select(func.count()).select_from(Appointment)) == 25
    rollback_preview = rollback_authorities(db, dry_run=True)
    assert rollback_preview.removed > 0
    assert db.scalar(select(func.count()).select_from(Appointment)) == 25
    rollback_authorities(db)
    assert db.scalar(select(func.count()).select_from(Person)) == 0
    assert db.scalar(select(func.count()).select_from(Appointment)) == 0


def test_consecutive_history_and_acting_capacity_are_representable() -> None:
    data = read_manifest()
    current = data["appointments"][0]
    history = dict(current, key="historical", end_date=date(2024, 8, 15).isoformat())
    acting = dict(current, key="acting", capacity="acting")
    assert history["end_date"] < current["start_date"]
    assert acting["capacity"] == "acting"
