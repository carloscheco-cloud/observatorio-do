import uuid

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.modules.evidence.models import Evidence
from app.modules.suppliers.models import Supplier, SupplierHistory
from app.modules.suppliers.schemas import SupplierCreate


def create_supplier(db: Session, payload: SupplierCreate, actor_type: str = "human") -> Supplier:
    if actor_type.lower() == "ai":
        raise PermissionError("AI actors cannot write canonical supplier data")
    evidence = db.get(Evidence, payload.evidence_id)
    if evidence is None or evidence.source_id != payload.source_id:
        raise ValueError("Evidence must exist and belong to the selected source")
    conditions = [Supplier.normalized_name == payload.normalized_name]
    if payload.registry_reference_hash:
        conditions.append(Supplier.registry_reference_hash == payload.registry_reference_hash)
    duplicate = db.scalar(select(Supplier).where(or_(*conditions)))
    if duplicate:
        raise ValueError("Potential duplicate supplier requires manual review")
    supplier = Supplier(**payload.model_dump(), actor_type=actor_type)
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


def list_suppliers(db: Session) -> list[Supplier]:
    return list(db.scalars(select(Supplier).order_by(Supplier.normalized_name)))


def history(db: Session, supplier_id: uuid.UUID) -> list[SupplierHistory]:
    return list(
        db.scalars(
            select(SupplierHistory)
            .where(SupplierHistory.supplier_id == supplier_id)
            .order_by(SupplierHistory.effective_date)
        )
    )
