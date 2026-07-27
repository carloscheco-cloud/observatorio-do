import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.asset_categories.models import AssetCategory
from app.modules.asset_categories.schemas import AssetCategoryCreate


def create_category(
    db: Session, payload: AssetCategoryCreate, actor_type: str = "human"
) -> AssetCategory:
    if actor_type.lower() == "ai":
        raise PermissionError("AI actors cannot write canonical asset categories")
    if payload.parent_id:
        parent = db.get(AssetCategory, payload.parent_id)
        if parent is None:
            raise ValueError("parent category not found")
    row = AssetCategory(**payload.model_dump(by_alias=False), actor_type=actor_type)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def descendants(db: Session, category_id: uuid.UUID) -> set[uuid.UUID]:
    found: set[uuid.UUID] = set()
    frontier = {category_id}
    while frontier:
        children = set(
            db.scalars(select(AssetCategory.id).where(AssetCategory.parent_id.in_(frontier)))
        )
        children -= found
        found |= children
        frontier = children
    return found
