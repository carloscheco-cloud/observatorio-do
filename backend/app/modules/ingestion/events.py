from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class IngestionEvent:
    name: str
    domain: str
    institution_id: str | None = None
    period: str | None = None


class EventDispatcher:
    allowed = {"ingestion_completed", "canonical_data_changed", "period_closed"}

    def __init__(self) -> None:
        self._handlers: list[Callable[[IngestionEvent], None]] = []

    def subscribe(self, handler: Callable[[IngestionEvent], None]) -> None:
        self._handlers.append(handler)

    def dispatch(self, event: IngestionEvent) -> None:
        if event.name not in self.allowed:
            raise ValueError("unsupported ingestion event")
        for handler in self._handlers:
            handler(event)
