from datetime import datetime
from typing import Any, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class Pagination(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool


class PublicCollection[T](BaseModel):
    data: list[T]
    pagination: Pagination
    filters_applied: dict[str, Any] = Field(default_factory=dict)
    sort: str
    generated_at: datetime
    source_freshness: str = "unknown"
    warnings: list[str] = Field(default_factory=list)


class PublicItem(BaseModel):
    data: dict[str, Any]
    generated_at: datetime
    source_freshness: str = "unknown"
    traceability: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class PublicError(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
    request_id: str
    timestamp: datetime


class InstitutionSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    kind: str
    territory_id: str
    status: str


class SearchResult(BaseModel):
    id: str
    entity_type: str
    title: str
    subtitle: str | None = None
    url: str
    score: float


class SeriesPoint(BaseModel):
    period: str
    value: float | None
    unit: str
    source: str | None = None
    status: str
    quality: str
    annotations: list[str] = Field(default_factory=list)
