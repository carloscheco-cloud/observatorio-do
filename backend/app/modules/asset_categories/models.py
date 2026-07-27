import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.db.base import Base

Json = JSON().with_variant(JSONB(), "postgresql")


class AssetCategory(Base):
    __tablename__ = "asset_categories"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    stable_code: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    official_name: Mapped[str] = mapped_column(String(300))
    normalized_name: Mapped[str] = mapped_column(String(300), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    category_type: Mapped[str] = mapped_column(String(50), index=True)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("asset_categories.id"))
    depreciation_method: Mapped[str | None] = mapped_column(String(40))
    default_useful_life_years: Mapped[int | None] = mapped_column(Integer)
    is_depreciable: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[str] = mapped_column(String(30), default="draft", index=True)
    valid_from: Mapped[date] = mapped_column(Date)
    valid_to: Mapped[date | None] = mapped_column(Date)
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sources.id"))
    evidence_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("evidence.id"))
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", Json, default=dict)
    actor_type: Mapped[str] = mapped_column(String(30), default="human")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
