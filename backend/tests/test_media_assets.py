import uuid

from sqlalchemy.orm import Session

from app.modules.institutions.models import Institution
from app.modules.media_assets import service
from app.modules.media_assets.models import MediaApprovalStatus, MediaAsset, MediaAssetType
from app.modules.territories.models import Territory, TerritoryType


def _institution(db: Session) -> Institution:
    territory = Territory(name="República Dominicana", code="DO", type=TerritoryType.COUNTRY)
    db.add(territory)
    db.flush()
    institution = Institution(
        name="Ministerio de Prueba",
        kind="ministry",
        slug="ministerio-prueba",
        territory_id=territory.id,
    )
    db.add(institution)
    db.flush()
    return institution


def _asset(
    institution: Institution,
    *,
    status: MediaApprovalStatus,
    source_url: str,
    is_primary: bool = False,
) -> MediaAsset:
    return MediaAsset(
        id=uuid.uuid4(),
        institution_id=institution.id,
        asset_type=MediaAssetType.INSTITUTION_BUILDING.value,
        storage_kind="remote_official",
        source_url=source_url,
        public_url=source_url,
        source_name="Portal institucional oficial",
        approval_status=status.value,
        is_primary=is_primary,
        alt_text="Edificio institucional de prueba",
    )


def test_public_service_exposes_only_approved_assets(db: Session) -> None:
    institution = _institution(db)
    approved = _asset(
        institution,
        status=MediaApprovalStatus.APPROVED,
        source_url="https://example.gob.do/approved.jpg",
        is_primary=True,
    )
    pending = _asset(
        institution,
        status=MediaApprovalStatus.PENDING,
        source_url="https://example.gob.do/pending.jpg",
    )
    rejected = _asset(
        institution,
        status=MediaApprovalStatus.REJECTED,
        source_url="https://example.gob.do/rejected.jpg",
    )
    archived = _asset(
        institution,
        status=MediaApprovalStatus.ARCHIVED,
        source_url="https://example.gob.do/archived.jpg",
    )
    db.add_all([approved, pending, rejected, archived])
    db.commit()

    items = service.for_institution(db, institution.slug or "")

    assert items is not None
    assert [item["id"] for item in items] == [str(approved.id)]
    assert items[0]["public_url"] == approved.public_url
    assert "approval_status" not in items[0]
    assert "approved_by" not in items[0]
    assert "checksum" not in items[0]


def test_public_service_returns_empty_collection_for_fallback(db: Session) -> None:
    institution = _institution(db)
    db.commit()

    items = service.for_institution(db, institution.slug or "")

    assert items == []


def test_public_service_returns_none_for_unknown_entities(db: Session) -> None:
    assert service.for_institution(db, "institucion-inexistente") is None
    assert service.for_person(db, str(uuid.uuid4())) is None
    assert service.by_id(db, str(uuid.uuid4())) is None


def test_public_service_rejects_malformed_identifiers(db: Session) -> None:
    assert service.for_person(db, "no-es-un-uuid") is None
    assert service.by_id(db, "no-es-un-uuid") is None
