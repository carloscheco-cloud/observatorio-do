from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.media_assets import service
from app.modules.media_assets.schemas import PublicMediaAsset, PublicMediaCollection

router = APIRouter(prefix="/executive", tags=["Executive Public Media"])
Db = Annotated[Session, Depends(get_db)]


def _collection(items: list[dict[str, object]]) -> PublicMediaCollection:
    return PublicMediaCollection.model_validate(
        {
            "items": items,
            "fallback_required": not items,
            "limitation": service.PUBLIC_LIMITATION,
        }
    )


@router.get(
    "/institutions/{slug}/media",
    response_model=PublicMediaCollection,
    summary="Activos visuales aprobados de una institución",
)
def institution_media(slug: str, db: Db) -> PublicMediaCollection:
    items = service.for_institution(db, slug)
    if items is None:
        raise HTTPException(
            404,
            detail={
                "code": "institution_not_found",
                "message": "La institución no fue localizada en los datos públicos.",
            },
        )
    return _collection(items)


@router.get(
    "/authorities/{person_id}/media",
    response_model=PublicMediaCollection,
    summary="Retratos oficiales aprobados de una autoridad",
)
def authority_media(person_id: str, db: Db) -> PublicMediaCollection:
    items = service.for_person(db, person_id)
    if items is None:
        raise HTTPException(
            404,
            detail={
                "code": "person_not_found",
                "message": "La persona no fue localizada en los datos públicos.",
            },
        )
    return _collection(items)


@router.get(
    "/media/{asset_id}",
    response_model=PublicMediaAsset,
    summary="Metadatos públicos de un activo visual aprobado",
)
def media_asset(asset_id: str, db: Db) -> PublicMediaAsset:
    item = service.by_id(db, asset_id)
    if item is None:
        raise HTTPException(
            404,
            detail={
                "code": "media_asset_not_found",
                "message": "El activo visual aprobado no fue localizado.",
            },
        )
    return PublicMediaAsset.model_validate(item)
