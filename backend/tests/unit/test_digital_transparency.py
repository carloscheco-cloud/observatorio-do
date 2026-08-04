from datetime import datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.modules.digital_transparency.methodology import (
    WEIGHTS,
    ComponentInput,
    appointment_act_score,
    calculate,
    classification,
    maturity,
    public_classification,
)
from app.modules.digital_transparency.models import InformationRequestStatus, VerificationStatus
from app.modules.digital_transparency.schemas import (
    InformationRequestCreate,
    is_definitive_broken_link,
)


def test_methodology_weights_sum_to_100_and_ranges() -> None:
    assert sum(WEIGHTS.values()) == Decimal("100")
    assert (
        appointment_act_score(
            act_located=True, downloadable=True, searchable=True, has_metadata=True
        )
        == 20
    )
    assert appointment_act_score(act_located=True) == 16
    assert appointment_act_score(act_located=False, appointment_verified=True) == 12
    assert appointment_act_score(act_located=False, authority_verified=True) == 6
    with pytest.raises(ValueError, match="outside"):
        calculate([ComponentInput("stable_links", Decimal("6"))])


def test_normalization_excludes_not_applicable_and_requires_components() -> None:
    result = calculate(
        [
            ComponentInput("institutional_identity", Decimal("10")),
            ComponentInput("stable_links", Decimal("0"), applicable=False),
        ]
    )
    assert result.raw_score == 10
    assert result.maximum_score == 10
    assert result.normalized_score == 100
    with pytest.raises(ValueError, match="requires components"):
        calculate([])


@pytest.mark.parametrize(
    "score,label",
    [
        (Decimal("90"), "disponibilidad digital avanzada"),
        (Decimal("75"), "disponibilidad digital alta"),
        (Decimal("60"), "disponibilidad digital intermedia"),
        (Decimal("40"), "disponibilidad digital limitada"),
        (Decimal("0"), "disponibilidad digital muy limitada"),
    ],
)
def test_descriptive_classification(score: Decimal, label: str) -> None:
    assert classification(score) == label


def test_maturity_blocks_public_band_and_ranking_scope_below_60_percent() -> None:
    assert maturity(Decimal("45")) == "partial"
    assert public_classification(Decimal("91.111"), Decimal("45")) == "evaluación parcial"
    assert maturity(Decimal("60")) == "provisional"
    assert public_classification(Decimal("75"), Decimal("60")) == "disponibilidad digital alta"
    assert maturity(Decimal("90")) == "complete"


def test_not_located_is_not_not_published() -> None:
    assert (
        VerificationStatus.NOT_LOCATED_IN_REVIEWED_SOURCES.value
        == "not_located_in_reviewed_sources"
    )
    assert "not_published" not in {item.value for item in VerificationStatus}


def test_saip_draft_has_no_fictitious_submission() -> None:
    draft = InformationRequestCreate(
        institution_id="x", subject="Acto", status=InformationRequestStatus.DRAFT
    )
    assert draft.submitted_at is None and draft.tracking_code is None
    with pytest.raises(ValidationError):
        InformationRequestCreate(
            institution_id="x", subject="Acto", status=InformationRequestStatus.SUBMITTED
        )
    submitted = InformationRequestCreate(
        institution_id="x",
        subject="Acto",
        status=InformationRequestStatus.SUBMITTED,
        submitted_at=datetime(2026, 8, 3),
    )
    assert submitted.submitted_at is not None


def test_broken_link_differs_from_temporary_unavailability() -> None:
    assert not is_definitive_broken_link([VerificationStatus.SOURCE_UNAVAILABLE], [None])
    assert is_definitive_broken_link([VerificationStatus.BROKEN_LINK], [404])
    assert is_definitive_broken_link([VerificationStatus.BROKEN_LINK] * 2, [None, None])
