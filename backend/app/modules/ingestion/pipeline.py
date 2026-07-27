from __future__ import annotations

import hashlib
import hmac
import re
import unicodedata
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation


@dataclass(frozen=True)
class Transformation:
    original: object
    normalized: object
    name: str
    version: str = "1"
    warnings: tuple[str, ...] = ()


class NormalizationPipeline:
    def __init__(self, sensitive_salt: str | None = None) -> None:
        self.sensitive_salt = sensitive_salt

    def apply(self, value: object, transformation: str, **config: object) -> Transformation:
        original = value
        warning: tuple[str, ...] = ()
        if transformation == "trim":
            value = str(value).strip()
        elif transformation == "unicode":
            value = unicodedata.normalize("NFKC", str(value))
        elif transformation == "lower":
            value = str(value).strip().lower()
        elif transformation == "upper":
            value = str(value).strip().upper()
        elif transformation == "proper_name":
            value = " ".join(part.capitalize() for part in str(value).strip().split())
        elif transformation == "decimal":
            try:
                value = Decimal(str(value).replace(",", ""))
            except InvalidOperation:
                value, warning = None, ("invalid decimal",)
        elif transformation == "percentage":
            try:
                value = Decimal(str(value).replace("%", "").strip()) / Decimal(100)
            except InvalidOperation:
                value, warning = None, ("invalid percentage",)
        elif transformation == "boolean":
            lookup = {
                "true": True,
                "1": True,
                "yes": True,
                "si": True,
                "false": False,
                "0": False,
                "no": False,
            }
            value = lookup.get(str(value).strip().lower())
            if value is None:
                warning = ("unknown boolean",)
        elif transformation == "null":
            configured_nulls = config.get("values", ["", "n/a", "null"])
            if not isinstance(configured_nulls, Iterable):
                raise ValueError("null values must be iterable")
            nulls = {str(item).lower() for item in configured_nulls}
            value = None if str(value).strip().lower() in nulls else value
        elif transformation == "date":
            try:
                value = date.fromisoformat(str(value).strip())
            except ValueError:
                value, warning = None, ("invalid ISO date",)
        elif transformation == "code":
            value = re.sub(r"[^A-Z0-9_-]", "", str(value).strip().upper())
        elif transformation == "sensitive_hash":
            if not self.sensitive_salt:
                raise ValueError("sensitive hash requires an environment-provided salt")
            value = hmac.new(
                self.sensitive_salt.encode(), str(value).strip().encode(), hashlib.sha256
            ).hexdigest()
        else:
            raise ValueError(f"unknown transformation: {transformation}")
        return Transformation(original, value, transformation, warnings=warning)


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    severity: str
    field: str | None
    message: str


class ValidationPipeline:
    def validate(
        self,
        row: dict[str, object],
        *,
        required: set[str] | None = None,
        types: dict[str, type[object]] | None = None,
        rules: list[Callable[[dict[str, object]], ValidationIssue | None]] | None = None,
    ) -> list[ValidationIssue]:
        issues = [
            ValidationIssue("required_missing", "error", field, "required value is absent")
            for field in required or set()
            if field not in row or row[field] is None or row[field] == ""
        ]
        for field, expected in (types or {}).items():
            if field in row and row[field] is not None and not isinstance(row[field], expected):
                issues.append(ValidationIssue("invalid_type", "error", field, expected.__name__))
        issues.extend(issue for rule in rules or [] if (issue := rule(row)) is not None)
        return issues


@dataclass(frozen=True)
class ChangeSet:
    added: set[str]
    removed: set[str]
    modified: set[str]
    unchanged: set[str]
    schema_changed: bool
    unexpected_volume_change: bool


class ChangeDetectionService:
    def compare(
        self,
        previous: dict[str, dict[str, object]],
        current: dict[str, dict[str, object]],
        *,
        volume_threshold: Decimal = Decimal("0.5"),
    ) -> ChangeSet:
        old_keys, new_keys = set(previous), set(current)
        common = old_keys & new_keys
        modified = {key for key in common if previous[key] != current[key]}
        schemas = {tuple(sorted(row)) for row in [*previous.values(), *current.values()]}
        baseline = max(len(previous), 1)
        volume_change = abs(len(current) - len(previous)) / baseline
        return ChangeSet(
            new_keys - old_keys,
            old_keys - new_keys,
            modified,
            common - modified,
            len(schemas) > 1,
            Decimal(str(volume_change)) > volume_threshold,
        )


@dataclass(frozen=True)
class MatchCandidate:
    entity_id: str
    method: str
    confidence: Decimal
    features: dict[str, object]


class EntityResolver:
    supported_types = {
        "institution",
        "territory",
        "person",
        "supplier",
        "position",
        "unit",
        "creditor",
        "asset",
        "contract",
        "process",
        "program",
        "classifier",
    }

    def resolve(
        self, entity_type: str, incoming: dict[str, object], candidates: list[dict[str, object]]
    ) -> list[MatchCandidate]:
        if entity_type not in self.supported_types:
            raise ValueError("unsupported entity type")
        results: list[MatchCandidate] = []
        for candidate in candidates:
            method, score = "none", Decimal("0")
            for key in ("stable_id", "external_reference", "hash"):
                if incoming.get(key) and incoming.get(key) == candidate.get(key):
                    method, score = key, Decimal("1")
                    break
            if score == 0 and incoming.get("normalized_name") == candidate.get("normalized_name"):
                method, score = "normalized_name", Decimal("0.90")
            if score:
                results.append(MatchCandidate(str(candidate["id"]), method, score, {"key": method}))
        return sorted(results, key=lambda item: item.confidence, reverse=True)
