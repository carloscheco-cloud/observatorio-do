from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.sources.models import Source
from app.modules.sources.schemas import SourceCreate


def list_sources(db: Session) -> list[Source]:
    return list(db.scalars(select(Source).order_by(Source.name)))


def create_source(db: Session, payload: SourceCreate) -> Source:
    source = Source(**payload.model_dump(mode="json"))
    db.add(source)
    db.commit()
    db.refresh(source)
    return source
