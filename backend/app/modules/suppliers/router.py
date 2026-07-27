import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.procurement_processes.models import ProcurementContract
from app.modules.procurement_processes.schemas import ContractRead
from app.modules.suppliers import service
from app.modules.suppliers.models import Supplier, SupplierHistory
from app.modules.suppliers.schemas import SupplierCreate, SupplierHistoryRead, SupplierRead

router = APIRouter(tags=["public procurement suppliers"])
Db = Annotated[Session, Depends(get_db)]
Actor = Annotated[str, Header(alias="X-Actor-Type")]


@router.get("/suppliers", response_model=list[SupplierRead])
def suppliers(db: Db) -> list[Supplier]:
    return service.list_suppliers(db)


@router.post("/suppliers", response_model=SupplierRead, status_code=201)
def create(payload: SupplierCreate, db: Db, actor: Actor = "human") -> Supplier:
    try:
        return service.create_supplier(db, payload, actor)
    except (ValueError, PermissionError) as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/suppliers/{supplier_id}", response_model=SupplierRead)
def get_supplier(supplier_id: uuid.UUID, db: Db) -> Supplier:
    row = db.get(Supplier, supplier_id)
    if row is None:
        raise HTTPException(404, "Supplier not found")
    return row


@router.get("/suppliers/{supplier_id}/history", response_model=list[SupplierHistoryRead])
def supplier_history(supplier_id: uuid.UUID, db: Db) -> list[SupplierHistory]:
    return service.history(db, supplier_id)


@router.get("/suppliers/{supplier_id}/contracts", response_model=list[ContractRead])
def supplier_contracts(supplier_id: uuid.UUID, db: Db) -> list[ProcurementContract]:
    return list(
        db.scalars(
            select(ProcurementContract).where(ProcurementContract.supplier_id == supplier_id)
        )
    )
