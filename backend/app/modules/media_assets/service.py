import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.institutions.models import Institution
from app.modules.media_assets.models import MediaApprovalStatus, MediaAsset
from app.modules.persons.models import Person

PUBLIC_LIMITATION = (
    "Solo se publican activos aprobados y trazables. La ausencia de una imagen aprobada activa "
    "un fallback visual y no implica que no exista una imagen oficial."
)


def _public_url(asset: MediaAsset) -> str | None:
    return asset.public_url or asset.source_url


def _serialize(asset: MediaAsset) -> dict[str, object] | None:
    public_url = _public_url(asset)
    if not public_url:
        return None
    return {
        "id": str(asset.id),
        "asset_type": asset.asset_type,
        "public_url": public_url,
        "source_url": asset.source_url,
        "source_name": asset.source_name,
        "verified_at": asset.verified_at,
        "is_primary": asset.is_primary,
        "alt_text": asset.alt_text,
        "caption": asset.caption,
        "license_note": asset.license_note,
        "width": asset.width,
        "height": asset.height,
    }


def _approved_assets(db: Session, *filters: object) -> list[dict[str, object]]:
    rows = db.scalars(
        select(MediaAsset)
        .where(
            MediaAsset.approval_status == MediaApprovalStatus.APPROVED.value,
            *filters,
        )
        .order_by(MediaAsset.is_primary.desc(), MediaAsset.asset_type, MediaAsset.created_at.desc())
    ).all()
    return [serialized for row in rows if (serialized := _serialize(row)) is not None]


def for_institution(db: Session, slug: str) -> list[dict[str, object]] | None:
    institution = db.scalar(select(Institution).where(Institution.slug == slug))
    if institution is None:
        return None
    return _approved_assets(db, MediaAsset.institution_id == institution.id)


def for_person(db: Session, person_id: str) -> list[dict[str, object]] | None:
    try:
        parsed_id = uuid.UUID(person_id)
    except ValueError:
        return None
    person = db.get(Person, parsed_id)
    if person is None:
        return None
    return _approved_assets(db, MediaAsset.person_id == person.id)


def by_id(db: Session, asset_id: str) -> dict[str, object] | None:
    try:
        parsed_id = uuid.UUID(asset_id)
    except ValueError:
        return None
    asset = db.scalar(
        select(MediaAsset).where(
            MediaAsset.id == parsed_id,
            MediaAsset.approval_status == MediaApprovalStatus.APPROVED.value,
        )
    )
    return _serialize(asset) if asset else None
