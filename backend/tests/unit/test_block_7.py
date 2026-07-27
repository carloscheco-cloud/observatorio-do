import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.modules.procurement_processes.ingestion import CsvProcurementImporter
from app.modules.procurement_processes.models import ProcurementType
from app.modules.procurement_processes.schemas import (
    AmendmentCreate,
    ContractCreate,
    PaymentCreate,
    ProcessCreate,
)
from app.modules.suppliers.schemas import SupplierCreate

ID = uuid.uuid4()


def process(**overrides: object) -> ProcessCreate:
    values: dict[str, object] = {
        "institution_id": ID,
        "process_code": "TEST-B7-001",
        "title": "Controlled fictitious purchase",
        "procurement_type": "goods",
        "procedure_type": "price_comparison",
        "process_status": "published",
        "publication_date": datetime(2099, 1, 1, tzinfo=UTC),
        "submission_deadline": datetime(2099, 1, 10, tzinfo=UTC),
        "opening_date": datetime(2099, 1, 11, tzinfo=UTC),
        "estimated_amount": Decimal("100.00"),
        "currency": "DOP",
        "fiscal_year": 2099,
        "source_id": uuid.uuid4(),
        "evidence_id": uuid.uuid4(),
    }
    values.update(overrides)
    return ProcessCreate.model_validate(values)


def test_process_creation_and_privacy() -> None:
    payload = process(raw_payload={"private": "controlled"})
    assert payload.estimated_amount == Decimal("100.00")
    assert "raw_payload" not in payload.model_dump()


def test_process_rejects_negative_amount_and_bad_dates() -> None:
    with pytest.raises(ValidationError):
        process(estimated_amount=-1)
    with pytest.raises(ValidationError):
        process(
            submission_deadline=datetime(2098, 12, 31, tzinfo=UTC),
        )


def test_supplier_requires_irreversible_reference_hash() -> None:
    with pytest.raises(ValidationError):
        SupplierCreate(
            legal_name="Proveedor Ficticio",
            normalized_name="proveedor ficticio",
            supplier_type="company",
            registry_reference_hash="plaintext-rnc",
            source_id=uuid.uuid4(),
            evidence_id=uuid.uuid4(),
        )


def test_supplier_normalized_name_is_canonical() -> None:
    with pytest.raises(ValidationError):
        SupplierCreate(
            legal_name="Proveedor Ficticio",
            normalized_name="Proveedor Ficticio",
            supplier_type="company",
            source_id=uuid.uuid4(),
            evidence_id=uuid.uuid4(),
        )


def test_contract_validates_dates_and_payment_ceiling() -> None:
    values = {
        "procurement_process_id": uuid.uuid4(),
        "award_id": uuid.uuid4(),
        "institution_id": uuid.uuid4(),
        "supplier_id": uuid.uuid4(),
        "contract_code": "CONTRACT-TEST",
        "title": "Controlled contract",
        "signature_date": date(2099, 1, 1),
        "start_date": date(2099, 1, 2),
        "end_date": date(2099, 12, 31),
        "original_amount": 100,
        "current_amount": 100,
        "paid_amount": 101,
        "currency": "DOP",
        "contract_status": "active",
        "procurement_type": ProcurementType.GOODS,
        "source_id": uuid.uuid4(),
        "evidence_id": uuid.uuid4(),
    }
    with pytest.raises(ValidationError):
        ContractCreate.model_validate(values)
    values["exception_documented"] = True
    assert ContractCreate.model_validate(values).paid_amount == 101


def test_amendment_cannot_leave_negative_amount() -> None:
    with pytest.raises(ValidationError):
        AmendmentCreate(
            contract_id=uuid.uuid4(),
            amendment_number="1",
            amendment_type="amount_decrease",
            effective_date=date(2099, 1, 1),
            previous_amount=100,
            new_amount=-1,
            description="Controlled amendment",
            legal_basis_id=uuid.uuid4(),
            source_id=uuid.uuid4(),
            evidence_id=uuid.uuid4(),
            status="confirmed",
        )


def test_payment_net_amount_is_reconciled() -> None:
    values = {
        "contract_id": uuid.uuid4(),
        "institution_id": uuid.uuid4(),
        "supplier_id": uuid.uuid4(),
        "payment_reference": "PAY-TEST",
        "payment_date": date(2099, 1, 1),
        "gross_amount": 100,
        "deductions": 10,
        "net_amount": 90,
        "currency": "DOP",
        "status": "confirmed",
        "source_id": uuid.uuid4(),
        "evidence_id": uuid.uuid4(),
    }
    assert PaymentCreate.model_validate(values).net_amount == 90
    values["net_amount"] = 91
    with pytest.raises(ValidationError):
        PaymentCreate.model_validate(values)


def test_ingestion_is_dry_run_idempotent_and_sanitizes_formulas() -> None:
    content = b"process_code,title,estimated_amount,currency\nTEST-1,=malicious,100,DOP\n"
    importer = CsvProcurementImporter()
    first = importer.preview(content, mapping={})
    second = importer.preview(content, mapping={})
    assert first.checksum == second.checksum
    assert first.valid_rows == 1
    assert first.normalized_rows[0]["title"] == "'=malicious"


def test_ingestion_rejects_invalid_amount() -> None:
    preview = CsvProcurementImporter().preview(
        b"process_code,title,estimated_amount,currency\nTEST-1,X,-1,DOP\n",
        mapping={},
    )
    assert preview.rejected_rows == 1
    assert preview.valid_rows == 0
