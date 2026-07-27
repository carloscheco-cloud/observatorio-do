import uuid
from datetime import date, datetime
from enum import StrEnum

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.db.base import Base


class AccessMethod(StrEnum):
    ELECTION = "election"
    APPOINTMENT = "appointment"
    COMPETITION = "competition"
    EX_OFFICIO = "ex_officio"
    OTHER = "other"


class PositionStatus(StrEnum):
    DRAFT = "draft"
    CANONICAL = "canonical"
    INACTIVE = "inactive"


class Position(Base):
    __tablename__ = "positions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    institution_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("institutions.id", ondelete="RESTRICT"), nullable=False
    )
    organizational_unit_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("organizational_units.id", ondelete="RESTRICT")
    )
    official_name: Mapped[str] = mapped_column(String(300), nullable=False)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    position_type: Mapped[str] = mapped_column(String(100), nullable=False)
    hierarchy_level: Mapped[str] = mapped_column(String(100), nullable=False)
    access_method: Mapped[AccessMethod] = mapped_column(Enum(AccessMethod), nullable=False)
    legal_basis_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("legal_bases.id", ondelete="RESTRICT"), nullable=False
    )
    status: Mapped[PositionStatus] = mapped_column(
        Enum(PositionStatus), default=PositionStatus.DRAFT, nullable=False
    )
    valid_from: Mapped[date | None] = mapped_column(Date)
    valid_to: Mapped[date | None] = mapped_column(Date)
    single_occupant: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    metadata_: Mapped[dict[str, object]] = mapped_column(
        "metadata", JSON().with_variant(JSONB(), "postgresql"), default=dict, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
