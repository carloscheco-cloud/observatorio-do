import uuid
from datetime import date
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app
from app.modules.public_assets.ingestion import preview_csv
from app.modules.public_assets.schemas import (
    AssetCreate,
    AssignmentCreate,
    DisposalCreate,
    TransferCreate,
    ValuationCreate,
)
from app.modules.public_assets.service import hash_reference, sanitize_raw_payload

IDS = {
    key: uuid.uuid4() for key in ("institution", "other", "category", "source", "evidence", "legal")
}
TRACE = {"source_id": IDS["source"], "evidence_id": IDS["evidence"]}


def asset(**overrides: object) -> AssetCreate:
    values: dict[str, object] = {
        "owner_institution_id": IDS["institution"],
        "asset_category_id": IDS["category"],
        "asset_code": "B9-TEST-001",
        "official_name": "Activo ficticio",
        "normalized_name": "activo ficticio",
        "acquisition_method": "purchase",
        "original_cost": Decimal("100"),
        "current_book_value": Decimal("90"),
        "currency": "DOP",
        "quantity": Decimal("1"),
        "status": "active",
        "condition_status": "good",
        "ownership_status": "owned",
        **TRACE,
    }
    values.update(overrides)
    return AssetCreate.model_validate(values)


def test_asset_uses_decimal_and_excludes_raw_payload() -> None:
    payload = asset(raw_payload={"plate": "CONTROL-PLAIN"})
    assert payload.original_cost == Decimal("100")
    assert "raw_payload" not in payload.model_dump()


def test_asset_rejects_negative_values_and_invalid_dates() -> None:
    with pytest.raises(ValidationError):
        asset(original_cost=Decimal("-1"))
    with pytest.raises(ValidationError, match="commissioning_date"):
        asset(acquisition_date=date(2099, 2, 1), commissioning_date=date(2099, 1, 1))


def test_assignment_and_transfer_dates_and_parties() -> None:
    with pytest.raises(ValidationError, match="end_date"):
        AssignmentCreate(
            asset_id=uuid.uuid4(),
            institution_id=IDS["institution"],
            assignment_type="custody",
            start_date=date(2099, 2, 1),
            end_date=date(2099, 1, 1),
            **TRACE,
        )
    with pytest.raises(ValidationError, match="origin"):
        TransferCreate(
            asset_id=uuid.uuid4(),
            origin_institution_id=IDS["institution"],
            destination_institution_id=IDS["institution"],
            transfer_type="permanent",
            approval_date=date(2099, 1, 1),
            effective_date=date(2099, 1, 2),
            legal_basis_id=IDS["legal"],
            description="Transferencia ficticia",
            **TRACE,
        )


def test_valuation_formula_and_disposal_dates() -> None:
    with pytest.raises(ValidationError, match="net_book_value"):
        ValuationCreate(
            asset_id=uuid.uuid4(),
            valuation_date=date(2099, 1, 1),
            valuation_type="accounting",
            gross_value=100,
            accumulated_depreciation=10,
            impairment_amount=5,
            net_book_value=90,
            valuation_method="controlled",
            **TRACE,
        )
    with pytest.raises(ValidationError, match="effective_date"):
        DisposalCreate(
            asset_id=uuid.uuid4(),
            institution_id=IDS["institution"],
            disposal_type="write_off",
            approval_date=date(2099, 2, 1),
            effective_date=date(2099, 1, 1),
            book_value=0,
            reason="Control",
            legal_basis_id=IDS["legal"],
            status="confirmed",
            **TRACE,
        )


def test_privacy_hash_sanitization_and_csv_protection() -> None:
    assert len(hash_reference("CONTROL-VIN")) == 64
    assert sanitize_raw_payload({"vin": "CONTROL", "nested": {"serial": "X"}}) == {
        "vin": "[REDACTED]",
        "nested": {"serial": "[REDACTED]"},
    }
    content = b"code,cost,serial\nB9,10,=MALICIOUS\n"
    preview = preview_csv(
        content,
        {"code": "asset_code", "cost": "original_cost", "serial": "serial_reference"},
    )
    assert preview.accepted_rows == 1
    assert (
        preview.checksum
        == preview_csv(
            content,
            {"code": "asset_code", "cost": "original_cost", "serial": "serial_reference"},
        ).checksum
    )
    assert len(str(preview.normalized_rows[0]["serial_reference"])) == 64


def test_asset_routes_are_registered() -> None:
    paths = set(app.openapi()["paths"])
    assert "/api/v1/public-assets" in paths
    assert "/api/v1/asset-categories" in paths
    assert "/api/v1/physical-inventories/{item_id}/items" in paths
    response = TestClient(app).get("/openapi.json")
    assert response.status_code == 200
