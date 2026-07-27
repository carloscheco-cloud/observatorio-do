import uuid
from datetime import date, datetime
from enum import StrEnum

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.db.base import Base

Json = JSON().with_variant(JSONB(), "postgresql")


class SupplierType(StrEnum):
    COMPANY = "company"
    INDIVIDUAL = "individual"
    CONSORTIUM = "consortium"
    NONPROFIT = "nonprofit"
    COOPERATIVE = "cooperative"
    FOREIGN_COMPANY = "foreign_company"
    PUBLIC_ENTITY = "public_entity"
    OTHER = "other"


class Supplier(Base):
    __tablename__ = "suppliers"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    legal_name: Mapped[str] = mapped_column(String(300))
    normalized_name: Mapped[str] = mapped_column(String(300))
    trade_name: Mapped[str | None] = mapped_column(String(300))
    supplier_type: Mapped[SupplierType] = mapped_column(Enum(SupplierType))
    registry_reference_hash: Mapped[str | None] = mapped_column(String(64))
    country: Mapped[str] = mapped_column(String(2), default="DO")
    territory_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("territories.id"))
    registration_status: Mapped[str] = mapped_column(String(30))
    registration_date: Mapped[date | None] = mapped_column(Date)
    economic_activity: Mapped[str | None] = mapped_column(String(300))
    is_public_entity: Mapped[bool] = mapped_column(Boolean, default=False)
    is_nonprofit: Mapped[bool] = mapped_column(Boolean, default=False)
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sources.id"))
    evidence_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("evidence.id"))
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", Json, default=dict)
    actor_type: Mapped[str] = mapped_column(String(30), default="human")
    validation_status: Mapped[str] = mapped_column(String(30), default="confirmed")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SupplierHistory(Base):
    __tablename__ = "supplier_history"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    supplier_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("suppliers.id"))
    legal_name: Mapped[str] = mapped_column(String(300))
    normalized_name: Mapped[str] = mapped_column(String(300))
    registration_status: Mapped[str] = mapped_column(String(30))
    effective_date: Mapped[date] = mapped_column(Date)
    reason: Mapped[str] = mapped_column(Text)
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sources.id"))
    evidence_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("evidence.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
