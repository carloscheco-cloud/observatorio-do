from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.territories.models import Territory
from app.modules.territories.schemas import TerritoryCreate


def list_territories(db: Session) -> list[Territory]:
    return list(db.scalars(select(Territory).order_by(Territory.name)))


def create_territory(db: Session, payload: TerritoryCreate) -> Territory:
    territory = Territory(**payload.model_dump())
    db.add(territory)
    db.commit()
    db.refresh(territory)
    return territory
