import uuid
from enum import StrEnum

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TerritoryType(StrEnum):
    COUNTRY = "country"
    PROVINCE = "province"
    MUNICIPALITY = "municipality"


class Territory(Base):
    __tablename__ = "territories"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    type: Mapped[TerritoryType] = mapped_column(Enum(TerritoryType), nullable=False)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("territories.id"))
    parent: Mapped["Territory | None"] = relationship(remote_side=[id], back_populates="children")
    children: Mapped[list["Territory"]] = relationship(back_populates="parent")
