import uuid
from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.modules.creditors.schemas import CreditorCreate
from app.modules.public_debt.ingestion import preview_csv
from app.modules.public_debt.schemas import (
    CommitmentCreate,
    GuaranteeCreate,
    InstrumentCreate,
    ObligationCreate,
    PaymentCreate,
    TransferCreate,
)

IDS = {key: uuid.uuid4() for key in ("institution", "other", "source", "evidence", "legal")}
TRACE = {"source_id": IDS["source"], "evidence_id": IDS["evidence"]}


def test_creditor_requires_hashed_sensitive_reference() -> None:
    with pytest.raises(ValidationError):
        CreditorCreate(
            legal_name="Acreedor ficticio",
            normalized_name="ACREEDOR FICTICIO",
            creditor_type="commercial_bank",
            is_domestic=True,
            is_public_entity=False,
            registry_reference_hash="sensitive-plain-text",
            **TRACE,
        )


def test_instrument_rejects_invalid_dates_and_principal() -> None:
    with pytest.raises(ValidationError, match="maturity_date"):
        InstrumentCreate(
            debtor_institution_id=IDS["institution"],
            instrument_code="TEST",
            title="Ficticio",
            instrument_type="loan",
            debt_scope="municipal",
            origin="domestic",
            original_principal=Decimal("100"),
            current_principal=Decimal("101"),
            effective_date=date(2100, 1, 1),
            maturity_date=date(2099, 1, 1),
            interest_type="fixed",
            legal_basis_id=IDS["legal"],
            **TRACE,
        )


def test_payment_and_obligation_components_are_coherent() -> None:
    with pytest.raises(ValidationError, match="total_paid"):
        PaymentCreate(
            debt_instrument_id=uuid.uuid4(),
            debtor_institution_id=IDS["institution"],
            payment_reference="P-1",
            payment_date=date(2099, 1, 1),
            principal_paid=10,
            interest_paid=2,
            fees_paid=0,
            penalties_paid=0,
            total_paid=11,
            **TRACE,
        )
    with pytest.raises(ValidationError, match="outstanding_amount"):
        ObligationCreate(
            institution_id=IDS["institution"],
            obligation_code="O-1",
            obligation_type="accounts_payable",
            description="Ficticia",
            recognition_date=date(2099, 1, 1),
            original_amount=100,
            outstanding_amount=80,
            paid_amount=10,
            status="pending",
            **TRACE,
        )


def test_guarantee_transfer_and_commitment_guards() -> None:
    with pytest.raises(ValidationError, match="exposure"):
        GuaranteeCreate(
            guarantor_institution_id=IDS["institution"],
            guaranteed_entity_id=IDS["other"],
            guarantee_code="G-1",
            guarantee_type="payment_guarantee",
            issue_date=date(2099, 1, 1),
            guaranteed_amount=100,
            outstanding_exposure=101,
            status="active",
            legal_basis_id=IDS["legal"],
            **TRACE,
        )
    with pytest.raises(ValidationError, match="origin"):
        TransferCreate(
            origin_institution_id=IDS["institution"],
            destination_institution_id=IDS["institution"],
            transfer_code="T-1",
            transfer_type="grant",
            approval_date=date(2099, 1, 1),
            approved_amount=100,
            paid_amount=0,
            purpose="Ficticio",
            fiscal_year=2099,
            status="approved",
            legal_basis_id=IDS["legal"],
            **TRACE,
        )
    with pytest.raises(ValidationError, match="annual breakdown"):
        CommitmentCreate(
            institution_id=IDS["institution"],
            commitment_code="M-1",
            start_year=2099,
            end_year=2100,
            total_committed_amount=100,
            annual_breakdown={"2099": Decimal("40"), "2100": Decimal("40")},
            status="active",
            legal_basis_id=IDS["legal"],
            **TRACE,
        )


def test_controlled_ingestion_is_idempotent_and_protects_csv() -> None:
    content = b"amount,currency,note\n10.25,DOP,=FORMULA\n"
    first = preview_csv(content, {"amount": "amount", "currency": "currency", "note": "note"})
    second = preview_csv(content, {"amount": "amount", "currency": "currency", "note": "note"})
    assert first.checksum == second.checksum
    assert first.normalized_rows[0]["note"] == "'=FORMULA"
