import hashlib
import json
from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class ImportPreview:
    checksum: str
    valid_rows: int
    rejected_rows: int
    errors: list[str] = field(default_factory=list)
    normalized_rows: list[dict[str, object]] = field(default_factory=list)


class PayrollImporter(Protocol):
    """Contract for CSV, XLSX, JSON and official-portal adapters."""

    def preview(self, content: bytes, *, dry_run: bool = True) -> ImportPreview: ...


class JsonPayrollImporter:
    required_columns = {"listed_name", "gross_income", "total_deductions", "net_income"}

    def preview(self, content: bytes, *, dry_run: bool = True) -> ImportPreview:
        checksum = hashlib.sha256(content).hexdigest()
        try:
            rows = json.loads(content)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            return ImportPreview(checksum, 0, 1, [f"Invalid JSON: {exc}"])
        if not isinstance(rows, list):
            return ImportPreview(checksum, 0, 1, ["Root value must be a list"])
        normalized: list[dict[str, object]] = []
        errors: list[str] = []
        for number, row in enumerate(rows, start=1):
            if not isinstance(row, dict):
                errors.append(f"Row {number}: expected object")
                continue
            missing = self.required_columns - row.keys()
            if missing:
                errors.append(f"Row {number}: missing {', '.join(sorted(missing))}")
                continue
            normalized.append({str(key).strip().lower(): value for key, value in row.items()})
        return ImportPreview(checksum, len(normalized), len(errors), errors, normalized)
