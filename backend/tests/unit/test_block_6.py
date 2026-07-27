from datetime import date

import pytest
from pydantic import ValidationError

from app.modules.budget.ingestion import CsvBudgetImporter
from app.modules.budget.schemas import BudgetCycleCreate, ExecutionCreate, TransferCreate


def test_cycle_dates_and_confirmed_traceability() -> None:
    with pytest.raises(ValidationError):
        BudgetCycleCreate(
            fiscal_year=2099,
            jurisdiction="control",
            government_level="controlled",
            cycle_type="approved",
            start_date=date(2099, 2, 1),
            end_date=date(2099, 1, 1),
            status="confirmed",
        )


def test_execution_sequence_requires_documented_exception() -> None:
    with pytest.raises(ValidationError):
        ExecutionCreate(
            budget_cycle_id="00000000-0000-0000-0000-000000000001",
            institution_id="00000000-0000-0000-0000-000000000002",
            appropriation_id="00000000-0000-0000-0000-000000000003",
            execution_period="2099-01",
            period_start=date(2099, 1, 1),
            period_end=date(2099, 1, 31),
            initial_budget=100,
            current_budget=100,
            committed_amount=50,
            accrued_amount=60,
            paid_amount=70,
            available_balance=50,
        )


def test_transfer_parties_must_differ() -> None:
    identifier = "00000000-0000-0000-0000-000000000001"
    with pytest.raises(ValidationError):
        TransferCreate(
            budget_cycle_id=identifier,
            origin_institution_id=identifier,
            destination_institution_id=identifier,
            transfer_type="grant",
            amount=1,
            effective_date=date(2099, 1, 1),
            purpose="controlled",
            legal_basis_id=identifier,
            source_id=identifier,
            evidence_id=identifier,
        )


def test_csv_preview_is_idempotent_and_formula_safe() -> None:
    content = (
        b"approved_amount,classifier_code,period_start,period_end,note\n"
        b"100,C1,2099-01-01,2099-01-31,=DANGEROUS\n"
    )
    importer = CsvBudgetImporter()
    first = importer.preview(content, mapping={})
    second = importer.preview(content, mapping={})
    assert first.checksum == second.checksum
    assert first.valid_rows == 1
    assert first.normalized_rows[0]["note"] == "'=DANGEROUS"
