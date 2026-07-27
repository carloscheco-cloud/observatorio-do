from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.asset_categories import service
from app.modules.asset_categories.models import AssetCategory
from app.modules.asset_categories.schemas import AssetCategoryCreate, AssetCategoryRead

router = APIRouter(tags=["public asset categories"])
Db = Annotated[Session, Depends(get_db)]
Actor = Annotated[str, Header(alias="X-Actor-Type")]


@router.get("/asset-categories", response_model=list[AssetCategoryRead])
def categories(db: Db) -> list[AssetCategory]:
    return list(db.scalars(select(AssetCategory)))


@router.post("/asset-categories", response_model=AssetCategoryRead, status_code=201)
def post_category(payload: AssetCategoryCreate, db: Db, actor: Actor = "human") -> AssetCategory:
    try:
        return service.create_category(db, payload, actor)
    except (ValueError, PermissionError) as exc:
        raise HTTPException(422, str(exc)) from exc
