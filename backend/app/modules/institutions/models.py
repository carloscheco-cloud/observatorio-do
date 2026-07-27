import uuid
from enum import StrEnum

from sqlalchemy import Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class InstitutionStatus(StrEnum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"


class Institution(Base):
    __tablename__ = "institutions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(300), unique=True, nullable=False)
    kind: Mapped[str] = mapped_column(String(100), nullable=False)
    territory_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("territories.id"), nullable=False)
    status: Mapped[InstitutionStatus] = mapped_column(
        Enum(InstitutionStatus), default=InstitutionStatus.DRAFT, nullable=False
    )
    evidence_links: Mapped[list["InstitutionEvidence"]] = relationship(
        back_populates="institution", cascade="all, delete-orphan"
    )


class InstitutionEvidence(Base):
    __tablename__ = "institution_evidence"
    __table_args__ = (UniqueConstraint("institution_id", "evidence_id"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    institution_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False
    )
    evidence_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("evidence.id", ondelete="RESTRICT"), nullable=False
    )
    relation: Mapped[str] = mapped_column(String(100), default="supports_existence", nullable=False)
    institution: Mapped[Institution] = relationship(back_populates="evidence_links")
