import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.db.base import Base

Json = JSON().with_variant(JSONB(), "postgresql")


class Creditor(Base):
    __tablename__ = "creditors"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    legal_name: Mapped[str] = mapped_column(String(400))
    normalized_name: Mapped[str] = mapped_column(String(400), index=True)
    creditor_type: Mapped[str] = mapped_column(String(40))
    country: Mapped[str | None] = mapped_column(String(2))
    territory_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("territories.id"))
    is_domestic: Mapped[bool] = mapped_column(Boolean)
    is_public_entity: Mapped[bool] = mapped_column(Boolean)
    registry_reference_hash: Mapped[str | None] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(30))
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sources.id"))
    evidence_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("evidence.id"))
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", Json, default=dict)
    actor_type: Mapped[str] = mapped_column(String(30), default="human")
    validation_status: Mapped[str] = mapped_column(String(30), default="confirmed")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class CreditorHistory(Base):
    __tablename__ = "creditor_history"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    creditor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("creditors.id"), index=True)
    legal_name: Mapped[str] = mapped_column(String(400))
    status: Mapped[str] = mapped_column(String(30))
    effective_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    reason: Mapped[str] = mapped_column(String(500))
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sources.id"))
    evidence_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("evidence.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
