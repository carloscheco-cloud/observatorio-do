import uuid
from datetime import date, datetime
from enum import StrEnum

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.db.base import Base


class LegalInstrumentType(StrEnum):
    CONSTITUTION = "constitution"
    LAW = "law"
    DECREE = "decree"
    RESOLUTION = "resolution"
    REGULATION = "regulation"
    ORDINANCE = "ordinance"
    OTHER = "other"


class LegalBasis(Base):
    __tablename__ = "legal_bases"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    instrument_type: Mapped[LegalInstrumentType] = mapped_column(
        Enum(LegalInstrumentType), nullable=False
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    reference: Mapped[str] = mapped_column(String(300), unique=True, nullable=False)
    article: Mapped[str | None] = mapped_column(String(100))
    official_url: Mapped[str | None] = mapped_column(String(1000))
    evidence_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("evidence.id", ondelete="RESTRICT"), nullable=False
    )
    effective_from: Mapped[date | None] = mapped_column(Date)
    effective_to: Mapped[date | None] = mapped_column(Date)
    issuing_body: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    metadata_: Mapped[dict[str, object]] = mapped_column(
        "metadata", JSON().with_variant(JSONB(), "postgresql"), default=dict, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
