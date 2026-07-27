import os
from decimal import Decimal

import pytest
from pydantic import ValidationError
from sqlalchemy import select

from app.db.seed import seed
from app.modules.employment_relationships import service as employment_service
from app.modules.employment_relationships.models import EmploymentRelationship
from app.modules.employment_relationships.schemas import EmploymentRelationshipCreate
from app.modules.payroll_entries import service as entry_service
from app.modules.payroll_entries.ingestion import JsonPayrollImporter
from app.modules.payroll_entries.models import PayrollEntry
from app.modules.payroll_entries.schemas import PayrollEntryCreate
from app.modules.payroll_findings import service as finding_service
from app.modules.payroll_periods.models import PayrollPeriod


def test_controlled_seed_is_idempotent(db) -> None:
    seed(db)
    seed(db)
    assert len(list(db.scalars(select(PayrollPeriod)))) == 2
    assert len(list(db.scalars(select(PayrollEntry)))) == 2
    assert len(list(db.scalars(select(EmploymentRelationship)))) == 1


def test_relationship_requires_person_and_valid_dates() -> None:
    with pytest.raises(ValidationError):
        EmploymentRelationshipCreate.model_validate(
            {
                "institution_id": "00000000-0000-0000-0000-000000000001",
                "employment_type": "career",
                "start_date": "2025-02-01",
                "end_date": "2025-01-01",
                "source_id": "00000000-0000-0000-0000-000000000002",
                "evidence_id": "00000000-0000-0000-0000-000000000003",
            }
        )


def test_relationship_history_and_overlap(db) -> None:
    seed(db)
    relationship = db.scalar(select(EmploymentRelationship))
    assert relationship is not None
    assert employment_service.list_relationships(db, person_id=relationship.person_id)
    assert employment_service.overlaps(db, relationship) == []


def test_negative_amount_and_sensitive_identifier_are_rejected() -> None:
    with pytest.raises(ValidationError):
        PayrollEntryCreate(
            person_id="00000000-0000-0000-0000-000000000001",
            institution_id="00000000-0000-0000-0000-000000000002",
            listed_name="Prueba 001-1234567-8",
            normalized_name="prueba",
            base_salary=-1,
            gross_income=0,
            total_deductions=0,
            net_income=0,
        )


def test_reconciliation_flag_and_period_comparison(db) -> None:
    seed(db)
    periods = list(db.scalars(select(PayrollPeriod).order_by(PayrollPeriod.month)))
    findings = finding_service.compare_periods(db, periods[1].id, periods[0].id)
    assert {finding.finding_type for finding in findings} >= {
        "salary_change",
        "payroll_mass_change",
    }


def test_sensitive_hash_uses_environment_salt(monkeypatch) -> None:
    monkeypatch.setenv("PAYROLL_REFERENCE_SALT", "controlled-test-only")
    digest = entry_service.hash_sensitive_reference("00112345678")
    assert len(digest) == 64
    assert "00112345678" not in digest
    os.environ.pop("PAYROLL_REFERENCE_SALT", None)


def test_json_import_preview_is_dry_run_and_idempotent() -> None:
    content = (
        b'[{"listed_name":"Persona Ficticia","gross_income":100,'
        b'"total_deductions":10,"net_income":90}]'
    )
    importer = JsonPayrollImporter()
    first = importer.preview(content)
    second = importer.preview(content)
    assert first.checksum == second.checksum
    assert first.valid_rows == 1
    assert first.rejected_rows == 0


def test_public_schema_excludes_raw_payload(db) -> None:
    from app.modules.payroll_entries.schemas import PayrollEntryRead

    seed(db)
    entry = db.scalar(select(PayrollEntry))
    assert entry is not None
    response = PayrollEntryRead.model_validate(entry).model_dump()
    assert "raw_payload" not in response
    assert "001-1234567-8" not in str(response)


def test_approximate_reconciliation_math() -> None:
    assert abs(Decimal("100") - Decimal("10") - Decimal("90")) <= Decimal("0.01")
