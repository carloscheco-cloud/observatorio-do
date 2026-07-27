from __future__ import annotations

import csv
import io
import json
import zipfile
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from xml.etree import ElementTree

from app.modules.ingestion.security import safe_archive_name, safe_csv_value


class ParsingError(ValueError):
    pass


@dataclass(frozen=True)
class ParsedRow:
    values: dict[str, object]
    row_number: int
    source_path: str | None = None
    sheet: str | None = None
    page: int | None = None


@dataclass(frozen=True)
class ParsedTable:
    name: str
    columns: list[str]
    rows: list[ParsedRow]
    confidence: str = "high"


@dataclass(frozen=True)
class ParserResult:
    tables: list[ParsedTable]
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    needs_review: bool = False


class BaseParser(ABC):
    @abstractmethod
    def parse(self, content: bytes) -> ParserResult: ...


def _decode(content: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "cp1252"):
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise ParsingError("unsupported text encoding")


class CsvParser(BaseParser):
    def __init__(self, max_rows: int = 100_000, max_columns: int = 500) -> None:
        self.max_rows = max_rows
        self.max_columns = max_columns

    def parse(self, content: bytes) -> ParserResult:
        text = _decode(content)
        try:
            dialect = csv.Sniffer().sniff(text[:8192], delimiters=",;\t|")
        except csv.Error:
            dialect = csv.excel
        reader = csv.reader(io.StringIO(text, newline=""), dialect)
        try:
            headers = [h.strip() for h in next(reader)]
        except StopIteration as exc:
            raise ParsingError("CSV is empty") from exc
        if len(headers) > self.max_columns:
            raise ParsingError("column limit exceeded")
        if len(headers) != len(set(headers)) or any(not h for h in headers):
            raise ParsingError("empty or duplicate headers")
        rows: list[ParsedRow] = []
        for number, values in enumerate(reader, 2):
            if number - 1 > self.max_rows:
                raise ParsingError("row limit exceeded")
            if len(values) != len(headers):
                raise ParsingError(f"row {number} has an unexpected number of columns")
            rows.append(
                ParsedRow(
                    {
                        key: safe_csv_value(value)
                        for key, value in zip(headers, values, strict=True)
                    },
                    number,
                )
            )
        return ParserResult([ParsedTable("csv", headers, rows)])


class JsonParser(BaseParser):
    def __init__(self, path: str = "", max_depth: int = 30, max_bytes: int = 25_000_000):
        self.path, self.max_depth, self.max_bytes = path, max_depth, max_bytes

    def parse(self, content: bytes) -> ParserResult:
        if len(content) > self.max_bytes:
            raise ParsingError("JSON size limit exceeded")
        data: object = json.loads(_decode(content))

        def depth(value: object, current: int = 0) -> int:
            if current > self.max_depth:
                raise ParsingError("JSON depth limit exceeded")
            if isinstance(value, dict):
                return max((depth(v, current + 1) for v in value.values()), default=current)
            if isinstance(value, list):
                return max((depth(v, current + 1) for v in value), default=current)
            return current

        depth(data)
        selected = data
        for part in filter(None, self.path.split(".")):
            if not isinstance(selected, dict) or part not in selected:
                raise ParsingError(f"JSON path not found: {self.path}")
            selected = selected[part]
        if not isinstance(selected, list) or not all(isinstance(row, dict) for row in selected):
            raise ParsingError("configured JSON path must resolve to an array of objects")
        columns = list(dict.fromkeys(key for row in selected for key in row))
        rows = [
            ParsedRow(dict(row), index + 1, source_path=f"{self.path or '$'}[{index}]")
            for index, row in enumerate(selected)
        ]
        return ParserResult([ParsedTable("json", columns, rows)])


class ZipParser(BaseParser):
    def __init__(
        self, max_files: int = 100, max_uncompressed: int = 100_000_000, max_ratio: int = 100
    ) -> None:
        self.max_files, self.max_uncompressed, self.max_ratio = (
            max_files,
            max_uncompressed,
            max_ratio,
        )

    def inspect(self, content: bytes) -> list[tuple[str, bytes]]:
        try:
            archive = zipfile.ZipFile(io.BytesIO(content))
        except zipfile.BadZipFile as exc:
            raise ParsingError("corrupted ZIP") from exc
        infos = archive.infolist()
        if len(infos) > self.max_files:
            raise ParsingError("ZIP file-count limit exceeded")
        total = sum(info.file_size for info in infos)
        if total > self.max_uncompressed:
            raise ParsingError("ZIP uncompressed-size limit exceeded")
        result = []
        for info in infos:
            name = safe_archive_name(info.filename)
            ratio = info.file_size / max(info.compress_size, 1)
            if ratio > self.max_ratio:
                raise ParsingError("ZIP bomb risk")
            if info.is_dir():
                continue
            result.append((name, archive.read(info)))
        return result

    def parse(self, content: bytes) -> ParserResult:
        files = self.inspect(content)
        rows = [
            ParsedRow({"filename": name, "size": len(payload)}, index + 1, source_path=name)
            for index, (name, payload) in enumerate(files)
        ]
        return ParserResult([ParsedTable("archive", ["filename", "size"], rows)])


class XlsxParser(BaseParser):
    namespaces = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}

    def __init__(self, sheets: set[str] | None = None, max_rows: int = 100_000) -> None:
        self.sheets, self.max_rows = sheets, max_rows

    def parse(self, content: bytes) -> ParserResult:
        files = dict(ZipParser(max_files=1000, max_uncompressed=200_000_000).inspect(content))
        if "xl/vbaProject.bin" in files:
            raise ParsingError("macro-enabled workbooks require review")
        shared: list[str] = []
        if "xl/sharedStrings.xml" in files:
            root = ElementTree.fromstring(files["xl/sharedStrings.xml"])
            shared = ["".join(node.itertext()) for node in root.findall("x:si", self.namespaces)]
        workbook = ElementTree.fromstring(files["xl/workbook.xml"])
        names = [node.attrib["name"] for node in workbook.findall(".//x:sheet", self.namespaces)]
        tables: list[ParsedTable] = []
        for index, name in enumerate(names, 1):
            if self.sheets and name not in self.sheets:
                continue
            path = f"xl/worksheets/sheet{index}.xml"
            if path not in files:
                continue
            root = ElementTree.fromstring(files[path])
            raw_rows: list[list[object]] = []
            for row in root.findall(".//x:row", self.namespaces):
                values: list[object] = []
                for cell in row.findall("x:c", self.namespaces):
                    value = cell.find("x:v", self.namespaces)
                    raw = "" if value is None or value.text is None else value.text
                    values.append(shared[int(raw)] if cell.attrib.get("t") == "s" and raw else raw)
                raw_rows.append(values)
                if len(raw_rows) > self.max_rows:
                    raise ParsingError("XLSX row limit exceeded")
            if not raw_rows:
                continue
            headers = [str(value).strip() for value in raw_rows[0]]
            if len(headers) != len(set(headers)):
                raise ParsingError("duplicate XLSX headers")
            rows = [
                ParsedRow(dict(zip(headers, values, strict=False)), row_no, sheet=name)
                for row_no, values in enumerate(raw_rows[1:], 2)
            ]
            merged = root.find("x:mergeCells", self.namespaces) is not None
            tables.append(
                ParsedTable(name, headers, rows, confidence="medium" if merged else "high")
            )
        warnings = (
            ["merged cells detected"] if any(t.confidence == "medium" for t in tables) else []
        )
        return ParserResult(tables, warnings=warnings)


class PdfTableParser(BaseParser):
    def __init__(self, extractor: object | None = None, allow_ocr: bool = False) -> None:
        self.extractor, self.allow_ocr = extractor, allow_ocr

    def parse(self, content: bytes) -> ParserResult:
        if not content.startswith(b"%PDF-"):
            raise ParsingError("invalid PDF signature")
        if self.extractor is None:
            return ParserResult([], ["reliable table extraction unavailable"], needs_review=True)
        extracted = self.extractor(content)  # type: ignore[operator]
        tables = [
            ParsedTable(
                f"page-{page}-table-{number}",
                list(rows[0]) if rows else [],
                [
                    ParsedRow(dict(zip(rows[0], row, strict=False)), index + 2, page=page)
                    for index, row in enumerate(rows[1:])
                ],
                confidence="low",
            )
            for page, number, rows in extracted
        ]
        return ParserResult(
            tables, warnings=["PDF table extraction has low confidence"], needs_review=True
        )
