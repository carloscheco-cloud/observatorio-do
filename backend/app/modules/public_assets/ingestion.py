import csv
import hashlib
import io
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Protocol

MAX_IMPORT_BYTES = 10 * 1024 * 1024


@dataclass
class AssetImportPreview:
    checksum: str
    format: str
    total_rows: int
    accepted_rows: int
    errors: list[dict[str, object]] = field(default_factory=list)
    normalized_rows: list[dict[str, object]] = field(default_factory=list)
    dry_run: bool = True


class AssetImporter(Protocol):
    def preview(self, content: bytes, mapping: dict[str, str]) -> AssetImportPreview: ...


def protect_csv(value: str) -> str:
    return "'" + value if value.lstrip().startswith(("=", "+", "-", "@")) else value


def preview_csv(
    content: bytes, mapping: dict[str, str], *, dry_run: bool = True
) -> AssetImportPreview:
    if len(content) > MAX_IMPORT_BYTES:
        raise ValueError("import exceeds size limit")
    checksum = hashlib.sha256(content).hexdigest()
    try:
        rows = list(csv.DictReader(io.StringIO(content.decode("utf-8-sig"))))
    except (UnicodeDecodeError, csv.Error) as exc:
        raise ValueError("invalid CSV") from exc
    result = AssetImportPreview(checksum, "csv", len(rows), 0, dry_run=dry_run)
    for number, row in enumerate(rows, start=2):
        normalized: dict[str, object] = {
            target: protect_csv(row.get(source, "").strip()) for source, target in mapping.items()
        }
        try:
            for field_name in ("original_cost", "current_book_value", "quantity"):
                if field_name in normalized:
                    normalized[field_name] = str(Decimal(str(normalized[field_name])))
            for key in list(normalized):
                if any(term in key.casefold() for term in ("vin", "serial", "plate", "title")):
                    normalized[key] = hashlib.sha256(str(normalized[key]).encode()).hexdigest()
        except InvalidOperation as exc:
            result.errors.append({"row": number, "error": str(exc)})
            continue
        result.normalized_rows.append(normalized)
        result.accepted_rows += 1
    return result
