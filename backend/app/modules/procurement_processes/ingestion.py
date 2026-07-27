import csv
import hashlib
import io
import json
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Protocol


@dataclass(frozen=True)
class ProcurementImportPreview:
    checksum: str
    valid_rows: int
    rejected_rows: int
    errors: list[str] = field(default_factory=list)
    normalized_rows: list[dict[str, object]] = field(default_factory=list)


class ProcurementImporter(Protocol):
    """Contract for CSV, XLSX, JSON, tabular PDF, portals and public APIs."""

    def preview(
        self, content: bytes, *, mapping: dict[str, str], dry_run: bool = True
    ) -> ProcurementImportPreview: ...


def sanitize_cell(value: object) -> object:
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


class CsvProcurementImporter:
    max_size = 10 * 1024 * 1024
    required = {"process_code", "title", "estimated_amount", "currency"}

    def preview(
        self, content: bytes, *, mapping: dict[str, str], dry_run: bool = True
    ) -> ProcurementImportPreview:
        checksum = hashlib.sha256(content).hexdigest()
        if len(content) > self.max_size:
            return ProcurementImportPreview(checksum, 0, 1, ["File exceeds 10 MiB"])
        try:
            rows = csv.DictReader(io.StringIO(content.decode("utf-8-sig")))
            normalized: list[dict[str, object]] = []
            errors: list[str] = []
            for number, row in enumerate(rows, 2):
                item = {mapping.get(k, k).strip().lower(): sanitize_cell(v) for k, v in row.items()}
                missing = self.required - item.keys()
                try:
                    amount = Decimal(str(item.get("estimated_amount", "")))
                    if amount < 0:
                        raise InvalidOperation
                except InvalidOperation:
                    errors.append(f"Row {number}: invalid monetary amount")
                    continue
                if missing:
                    errors.append(f"Row {number}: missing {', '.join(sorted(missing))}")
                else:
                    normalized.append(item)
            return ProcurementImportPreview(
                checksum, len(normalized), len(errors), errors, normalized
            )
        except (UnicodeDecodeError, csv.Error, json.JSONDecodeError) as exc:
            return ProcurementImportPreview(checksum, 0, 1, [f"Invalid file: {exc}"])
