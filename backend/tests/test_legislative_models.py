from app.modules.legislative.models import (
    DataAvailability,
    LegislativeChamber,
    LegislativeMandate,
    LegislativeSeat,
)


def test_legislative_core_tables_are_registered() -> None:
    assert LegislativeChamber.__tablename__ == "legislative_chambers"
    assert LegislativeSeat.__tablename__ == "legislative_seats"
    assert LegislativeMandate.__tablename__ == "legislative_mandates"


def test_mandate_separates_unavailable_data_from_zero_metrics() -> None:
    columns = LegislativeMandate.__table__.columns

    assert "attendance_availability" in columns
    assert "voting_availability" in columns
    assert "initiatives_availability" in columns
    assert "coverage_score" in columns
    assert DataAvailability.NOT_AVAILABLE.value == "not_available"
    assert DataAvailability.AVAILABLE.value == "available"


def test_legislative_records_require_official_traceability() -> None:
    for model in (LegislativeChamber, LegislativeSeat, LegislativeMandate):
        columns = model.__table__.columns
        assert not columns["source_id"].nullable
        assert not columns["evidence_id"].nullable
        assert "validation_status" in columns
        assert "actor_type" in columns
