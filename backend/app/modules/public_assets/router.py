import uuid
from decimal import Decimal
from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.public_assets import service
from app.modules.public_assets.models import (
    AssetAssignment,
    AssetDisposal,
    AssetEvent,
    AssetFinding,
    AssetInsurancePolicy,
    AssetLocation,
    AssetMaintenanceRecord,
    AssetTransfer,
    AssetValuation,
    PhysicalInventory,
    PhysicalInventoryItem,
    PublicAsset,
)
from app.modules.public_assets.schemas import (
    AssetCreate,
    AssetMetrics,
    AssetRead,
    AssignmentCreate,
    DisposalCreate,
    FindingReview,
    GenericRead,
    InventoryCreate,
    LocationCreate,
    MaintenanceCreate,
    TransferCreate,
    ValuationCreate,
)

router = APIRouter(tags=["public assets and patrimony"])
Db = Annotated[Session, Depends(get_db)]
Actor = Annotated[str, Header(alias="X-Actor-Type")]


def _create(db: Session, model: type[Any], payload: Any, actor: str) -> Any:
    try:
        return service.create_canonical(db, model, payload, actor)
    except (ValueError, PermissionError) as exc:
        raise HTTPException(422, str(exc)) from exc


def _get(db: Session, model: type[Any], item_id: uuid.UUID) -> Any:
    row = db.get(model, item_id)
    if row is None:
        raise HTTPException(404, "Resource not found")
    return row


@router.get("/public-assets", response_model=list[AssetRead])
def assets(
    db: Db,
    institution_id: uuid.UUID | None = None,
    category_id: uuid.UUID | None = None,
    territory_id: uuid.UUID | None = None,
    location_id: uuid.UUID | None = None,
    organizational_unit_id: uuid.UUID | None = None,
    status: str | None = None,
    condition_status: str | None = None,
    acquisition_method: str | None = None,
    minimum_value: Decimal | None = None,
    maximum_value: Decimal | None = None,
) -> list[PublicAsset]:
    query = select(PublicAsset)
    filters = {
        "owner_institution_id": institution_id,
        "asset_category_id": category_id,
        "territory_id": territory_id,
        "location_id": location_id,
        "organizational_unit_id": organizational_unit_id,
        "status": status,
        "condition_status": condition_status,
        "acquisition_method": acquisition_method,
    }
    for key, value in filters.items():
        if value is not None:
            query = query.where(getattr(PublicAsset, key) == value)
    if minimum_value is not None:
        query = query.where(PublicAsset.current_book_value >= minimum_value)
    if maximum_value is not None:
        query = query.where(PublicAsset.current_book_value <= maximum_value)
    return list(db.scalars(query))


@router.post("/public-assets", response_model=AssetRead, status_code=201)
def post_asset(payload: AssetCreate, db: Db, actor: Actor = "human") -> Any:
    return _create(db, PublicAsset, payload, actor)


@router.get("/public-assets/{item_id}", response_model=AssetRead)
def asset(item_id: uuid.UUID, db: Db) -> PublicAsset:
    return cast(PublicAsset, _get(db, PublicAsset, item_id))


@router.get("/public-assets/{item_id}/history", response_model=list[GenericRead])
def history(item_id: uuid.UUID, db: Db) -> list[Any]:
    return service.asset_history(db, item_id)


def _children(db: Session, model: type[Any], item_id: uuid.UUID) -> list[Any]:
    return service.list_rows(db, model, asset_id=item_id)


@router.get("/public-assets/{item_id}/assignments", response_model=list[GenericRead])
def asset_assignments(item_id: uuid.UUID, db: Db) -> list[Any]:
    return _children(db, AssetAssignment, item_id)


@router.get("/public-assets/{item_id}/valuations", response_model=list[GenericRead])
def asset_valuations(item_id: uuid.UUID, db: Db) -> list[Any]:
    return _children(db, AssetValuation, item_id)


@router.get("/public-assets/{item_id}/maintenance", response_model=list[GenericRead])
def asset_maintenance(item_id: uuid.UUID, db: Db) -> list[Any]:
    return _children(db, AssetMaintenanceRecord, item_id)


@router.get("/public-assets/{item_id}/events", response_model=list[GenericRead])
def asset_events(item_id: uuid.UUID, db: Db) -> list[Any]:
    return _children(db, AssetEvent, item_id)


@router.get("/public-assets/{item_id}/insurance", response_model=list[GenericRead])
def asset_insurance(item_id: uuid.UUID, db: Db) -> list[Any]:
    return _children(db, AssetInsurancePolicy, item_id)


def _list_create(path: str, model: type[Any], schema: type[Any]) -> None:
    @router.get(path, response_model=list[GenericRead])
    def list_endpoint(db: Db) -> list[Any]:
        return service.list_rows(db, model)

    @router.post(path, response_model=GenericRead, status_code=201)
    def create_endpoint(payload: schema, db: Db, actor: Actor = "human") -> Any:  # type: ignore[valid-type]
        return _create(db, model, payload, actor)


_list_create("/asset-locations", AssetLocation, LocationCreate)
_list_create("/asset-transfers", AssetTransfer, TransferCreate)
_list_create("/asset-maintenance-records", AssetMaintenanceRecord, MaintenanceCreate)
_list_create("/asset-valuations", AssetValuation, ValuationCreate)
_list_create("/physical-inventories", PhysicalInventory, InventoryCreate)


@router.get("/asset-assignments", response_model=list[GenericRead])
def assignments(db: Db) -> list[Any]:
    return service.list_rows(db, AssetAssignment)


@router.post("/asset-assignments", response_model=GenericRead, status_code=201)
def post_assignment(payload: AssignmentCreate, db: Db, actor: Actor = "human") -> Any:
    try:
        return service.create_assignment(db, payload, actor)
    except (ValueError, PermissionError) as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/physical-inventories/{item_id}", response_model=GenericRead)
def inventory(item_id: uuid.UUID, db: Db) -> Any:
    return _get(db, PhysicalInventory, item_id)


@router.get("/physical-inventories/{item_id}/items", response_model=list[GenericRead])
def inventory_items(item_id: uuid.UUID, db: Db) -> list[Any]:
    return service.list_rows(db, PhysicalInventoryItem, physical_inventory_id=item_id)


@router.get("/asset-disposals", response_model=list[GenericRead])
def disposals(db: Db) -> list[Any]:
    return service.list_rows(db, AssetDisposal)


@router.post("/asset-disposals", response_model=GenericRead, status_code=201)
def post_disposal(payload: DisposalCreate, db: Db, actor: Actor = "human") -> Any:
    try:
        return service.create_disposal(db, payload, actor)
    except (ValueError, PermissionError) as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/asset-findings", response_model=list[GenericRead])
def findings(db: Db, finding_type: str | None = None, severity: str | None = None) -> list[Any]:
    return service.list_rows(db, AssetFinding, finding_type=finding_type, severity=severity)


@router.get("/asset-findings/{item_id}", response_model=GenericRead)
def finding(item_id: uuid.UUID, db: Db) -> Any:
    return _get(db, AssetFinding, item_id)


@router.patch("/asset-findings/{item_id}/review", response_model=GenericRead)
def review_finding(item_id: uuid.UUID, payload: FindingReview, db: Db) -> Any:
    row = finding(item_id, db)
    row.status, row.reviewer_notes = payload.status, payload.reviewer_notes
    db.commit()
    db.refresh(row)
    return row


@router.get("/institutions/{institution_id}/assets", response_model=list[AssetRead])
def institution_assets(institution_id: uuid.UUID, db: Db) -> list[PublicAsset]:
    return service.list_rows(db, PublicAsset, owner_institution_id=institution_id)


@router.get("/institutions/{institution_id}/asset-metrics", response_model=AssetMetrics)
def institution_metrics(institution_id: uuid.UUID, db: Db) -> AssetMetrics:
    return service.metrics(db, institution_id)


@router.get("/institutions/{institution_id}/asset-history", response_model=list[GenericRead])
def institution_history(institution_id: uuid.UUID, db: Db) -> list[Any]:
    return service.list_rows(db, AssetEvent, institution_id=institution_id)


@router.get(
    "/institutions/{institution_id}/assets-without-custodian", response_model=list[AssetRead]
)
def without_custodian(institution_id: uuid.UUID, db: Db) -> list[PublicAsset]:
    return list(
        db.scalars(
            select(PublicAsset).where(
                PublicAsset.owner_institution_id == institution_id,
                PublicAsset.custodian_person_id.is_(None),
            )
        )
    )


@router.get(
    "/institutions/{institution_id}/assets-without-recent-inventory", response_model=list[AssetRead]
)
def without_recent_inventory(institution_id: uuid.UUID, db: Db) -> list[PublicAsset]:
    inventoried = (
        select(PhysicalInventoryItem.asset_id)
        .join(PhysicalInventory)
        .where(PhysicalInventory.institution_id == institution_id)
    )
    return list(
        db.scalars(
            select(PublicAsset).where(
                PublicAsset.owner_institution_id == institution_id,
                PublicAsset.id.not_in(inventoried),
            )
        )
    )


@router.get("/institutions/{institution_id}/maintenance-overdue", response_model=list[GenericRead])
def overdue(institution_id: uuid.UUID, db: Db) -> list[Any]:
    return service.list_rows(
        db, AssetMaintenanceRecord, institution_id=institution_id, status="overdue"
    )
