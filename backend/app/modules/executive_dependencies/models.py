import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ExecutiveDependencyLoadRecord(Base):
    __tablename__ = "executive_dependency_load_records"
    __table_args__ = (
        UniqueConstraint(
            "manifest_version", "record_type", "record_id", name="uq_executive_dependency_record"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    manifest_version: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    record_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    record_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
