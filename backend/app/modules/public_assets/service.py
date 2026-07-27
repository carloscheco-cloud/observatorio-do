import hashlib
import uuid
from decimal import Decimal
from typing import Any, cast

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.organizational_units.models import OrganizationalUnit
from app.modules.positions.models import Position
from app.modules.public_assets.models import (
    AssetAssignment,
    AssetDisposal,
    AssetInsurancePolicy,
    AssetMaintenanceRecord,
    AssetValuation,
    PublicAsset,
)
from app.modules.public_assets.schemas import AssetMetrics, AssignmentCreate, DisposalCreate

DISPOSED = {"disposed", "written_off", "sold", "demolished"}
SENSITIVE_KEYS = {"plate", "vin", "chassis", "serial", "title", "policy_number"}


def hash_reference(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sanitize_raw_payload(value: object) -> object:
    if isinstance(value, dict):
        return {
            key: ("[REDACTED]" if key.casefold() in SENSITIVE_KEYS else sanitize_raw_payload(item))
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [sanitize_raw_payload(item) for item in value]
    return value


def _institution(db: Session, entity: object) -> uuid.UUID | None:
    if isinstance(entity, PublicAsset):
        return entity.managing_institution_id or entity.owner_institution_id
    return getattr(entity, "institution_id", None)


def _check_unit(db: Session, unit_id: uuid.UUID | None, institution_id: uuid.UUID) -> None:
    if unit_id is None:
        return
    unit = db.get(OrganizationalUnit, unit_id)
    if unit is None or unit.institution_id != institution_id:
        raise ValueError("organizational unit is incompatible with institution")


def create_canonical(
    db: Session, model: type[Any], payload: BaseModel, actor_type: str = "human"
) -> Any:
    if actor_type.lower() == "ai":
        raise PermissionError("AI actors cannot write canonical public-asset records")
    data = payload.model_dump(by_alias=False)
    if "raw_payload" in data:
        data["raw_payload"] = sanitize_raw_payload(data["raw_payload"])
    if "actor_type" in model.__table__.columns:
        data["actor_type"] = actor_type
    row = model(**data)
    institution_id = _institution(db, row)
    if institution_id:
        _check_unit(db, getattr(row, "organizational_unit_id", None), institution_id)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def create_assignment(db: Session, payload: AssignmentCreate, actor_type: str) -> AssetAssignment:
    asset = db.get(PublicAsset, payload.asset_id)
    if asset is None:
        raise ValueError("asset not found")
    if payload.institution_id not in {asset.owner_institution_id, asset.managing_institution_id}:
        raise ValueError("assignment institution is incompatible with asset")
    _check_unit(db, payload.organizational_unit_id, payload.institution_id)
    if payload.position_id:
        position = db.get(Position, payload.position_id)
        if position is None or position.institution_id != payload.institution_id:
            raise ValueError("position is incompatible with institution")
    if payload.status == "active":
        conflict = db.scalar(
            select(AssetAssignment.id).where(
                AssetAssignment.asset_id == payload.asset_id,
                AssetAssignment.status == "active",
                AssetAssignment.end_date.is_(None),
                AssetAssignment.assignment_type == payload.assignment_type,
            )
        )
        if conflict:
            raise ValueError("incompatible active assignment already exists")
    return cast(AssetAssignment, create_canonical(db, AssetAssignment, payload, actor_type))


def create_disposal(db: Session, payload: DisposalCreate, actor_type: str) -> AssetDisposal:
    asset = db.get(PublicAsset, payload.asset_id)
    if asset is None or asset.owner_institution_id != payload.institution_id:
        raise ValueError("asset is incompatible with institution")
    duplicate = db.scalar(
        select(AssetDisposal.id).where(
            AssetDisposal.asset_id == payload.asset_id,
            AssetDisposal.status.in_(("approved", "effective", "completed")),
        )
    )
    if duplicate:
        raise ValueError("active disposal already exists")
    assigned = db.scalar(
        select(AssetAssignment.id).where(
            AssetAssignment.asset_id == payload.asset_id,
            AssetAssignment.status == "active",
            AssetAssignment.end_date.is_(None),
        )
    )
    if assigned:
        raise ValueError("asset with active assignment cannot be disposed")
    return cast(AssetDisposal, create_canonical(db, AssetDisposal, payload, actor_type))


def list_rows(db: Session, model: type[Any], **filters: object) -> list[Any]:
    query = select(model)
    for key, value in filters.items():
        if value is not None:
            query = query.where(getattr(model, key) == value)
    return list(db.scalars(query))


def metrics(db: Session, institution_id: uuid.UUID) -> AssetMetrics:
    base = PublicAsset.owner_institution_id == institution_id

    def amount(column: Any) -> Decimal:
        return Decimal(db.scalar(select(func.coalesce(func.sum(column), 0)).where(base)) or 0)

    return AssetMetrics(
        asset_count=int(db.scalar(select(func.count()).select_from(PublicAsset).where(base)) or 0),
        original_value=amount(PublicAsset.original_cost),
        book_value=amount(PublicAsset.current_book_value),
        estimated_value=amount(PublicAsset.estimated_market_value),
        maintenance_cost=Decimal(
            db.scalar(
                select(func.coalesce(func.sum(AssetMaintenanceRecord.cost), 0)).where(
                    AssetMaintenanceRecord.institution_id == institution_id
                )
            )
            or 0
        ),
        without_custodian=int(
            db.scalar(
                select(func.count())
                .select_from(PublicAsset)
                .where(
                    base,
                    PublicAsset.custodian_person_id.is_(None),
                    ~PublicAsset.status.in_(DISPOSED),
                )
            )
            or 0
        ),
        insured_count=int(
            db.scalar(
                select(func.count(func.distinct(AssetInsurancePolicy.asset_id)))
                .join(PublicAsset, PublicAsset.id == AssetInsurancePolicy.asset_id)
                .where(base, AssetInsurancePolicy.status == "active")
            )
            or 0
        ),
    )


def asset_history(db: Session, asset_id: uuid.UUID) -> list[Any]:
    from app.modules.public_assets.models import AssetEvent, AssetVersion

    events = list_rows(db, AssetEvent, asset_id=asset_id)
    versions = list_rows(db, AssetVersion, new_entity_id=asset_id)
    return sorted([*events, *versions], key=lambda row: row.created_at)


def valuations(db: Session, asset_id: uuid.UUID) -> list[AssetValuation]:
    return list_rows(db, AssetValuation, asset_id=asset_id)
