from __future__ import annotations

import uuid
from collections.abc import Callable
from dataclasses import dataclass

from app.modules.ingestion.events import EventDispatcher, IngestionEvent


@dataclass(frozen=True)
class CanonicalizationResult:
    action: str
    entity_id: uuid.UUID
    evidence_id: uuid.UUID


class CanonicalizationService:
    def __init__(self, dispatcher: EventDispatcher | None = None) -> None:
        self.dispatcher = dispatcher or EventDispatcher()

    def canonicalize(
        self,
        *,
        actor_type: str,
        validation_status: str,
        domain: str,
        authorized_service: Callable[[dict[str, object], str], tuple[str, uuid.UUID]],
        evidence_service: Callable[[], uuid.UUID],
        normalized_data: dict[str, object],
    ) -> CanonicalizationResult:
        if actor_type == "ai":
            raise PermissionError("AI actors cannot confirm canonical records")
        if validation_status != "valid":
            raise ValueError("only valid staging records can be canonicalized")
        action, entity_id = authorized_service(normalized_data, actor_type)
        if action not in {"create", "update", "unchanged"}:
            raise ValueError("authorized service returned an invalid action")
        evidence_id = evidence_service()
        self.dispatcher.dispatch(IngestionEvent("canonical_data_changed", domain))
        return CanonicalizationResult(action, entity_id, evidence_id)


class InstitutionCanonicalizer(CanonicalizationService):
    pass


class PersonCanonicalizer(CanonicalizationService):
    pass


class OrganizationalCanonicalizer(CanonicalizationService):
    pass


class EmploymentCanonicalizer(CanonicalizationService):
    pass


class PayrollCanonicalizer(CanonicalizationService):
    pass


class BudgetCanonicalizer(CanonicalizationService):
    pass


class ProcurementCanonicalizer(CanonicalizationService):
    pass


class DebtCanonicalizer(CanonicalizationService):
    pass


class AssetCanonicalizer(CanonicalizationService):
    pass
