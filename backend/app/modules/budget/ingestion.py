import csv
import hashlib
import io
import json
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Protocol


@dataclass(frozen=True)
class BudgetImportPreview:
    checksum: str
    valid_rows: int
    rejected_rows: int
    errors: list[str] = field(default_factory=list)
    normalized_rows: list[dict[str, object]] = field(default_factory=list)


class BudgetImporter(Protocol):
    """Adapter contract for CSV, XLSX, JSON, tabular PDF, portals and APIs."""

    def preview(
        self, content: bytes, *, mapping: dict[str, str], dry_run: bool = True
    ) -> BudgetImportPreview: ...


def sanitize_cell(value: object) -> object:
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


class CsvBudgetImporter:
    max_size = 10 * 1024 * 1024
    required = {"approved_amount", "classifier_code", "period_start", "period_end"}

    def preview(
        self, content: bytes, *, mapping: dict[str, str], dry_run: bool = True
    ) -> BudgetImportPreview:
        checksum = hashlib.sha256(content).hexdigest()
        if len(content) > self.max_size:
            return BudgetImportPreview(checksum, 0, 1, ["File exceeds 10 MiB"])
        try:
            rows = csv.DictReader(io.StringIO(content.decode("utf-8-sig")))
            normalized: list[dict[str, object]] = []
            errors: list[str] = []
            for number, row in enumerate(rows, 2):
                item = {mapping.get(k, k).strip().lower(): sanitize_cell(v) for k, v in row.items()}
                missing = self.required - item.keys()
                try:
                    Decimal(str(item.get("approved_amount", "")))
                except InvalidOperation:
                    errors.append(f"Row {number}: invalid monetary amount")
                    continue
                if missing:
                    errors.append(f"Row {number}: missing {', '.join(sorted(missing))}")
                else:
                    normalized.append(item)
            return BudgetImportPreview(checksum, len(normalized), len(errors), errors, normalized)
        except (UnicodeDecodeError, csv.Error, json.JSONDecodeError) as exc:
            return BudgetImportPreview(checksum, 0, 1, [f"Invalid file: {exc}"])
