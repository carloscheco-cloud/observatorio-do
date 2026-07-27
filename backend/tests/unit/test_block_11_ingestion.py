from __future__ import annotations

import io
import json
import uuid
import zipfile
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.modules.ingestion.canonicalization import CanonicalizationService
from app.modules.ingestion.connectors import (
    HttpFileConnector,
    JsonApiConnector,
    ManualUploadConnector,
    detect_mime,
)
from app.modules.ingestion.events import EventDispatcher
from app.modules.ingestion.jobs import retry_delay
from app.modules.ingestion.parsers import (
    CsvParser,
    JsonParser,
    ParsingError,
    PdfTableParser,
    ZipParser,
)
from app.modules.ingestion.pipeline import (
    ChangeDetectionService,
    EntityResolver,
    NormalizationPipeline,
    ValidationPipeline,
)
from app.modules.ingestion.schemas import ScheduleCreate, SourceCatalogCreate
from app.modules.ingestion.security import (
    UnsafeSourceError,
    redact_configuration,
    safe_archive_name,
    safe_csv_value,
    validate_public_url,
)


def public_resolver(host: str, port: int, type: int) -> list[tuple[object, ...]]:
    return [(None, None, None, None, ("93.184.216.34", port))]


@pytest.mark.parametrize(
    "url",
    ["file:///etc/passwd", "http://localhost/a", "http://127.0.0.1", "http://169.254.169.254"],
)
def test_ssrf_and_protocols_are_blocked(url: str) -> None:
    with pytest.raises(UnsafeSourceError):
        validate_public_url(url)


def test_public_url_is_allowed_with_validated_dns() -> None:
    assert validate_public_url("https://example.test/data", public_resolver).startswith("https")


def test_source_configuration_rejects_embedded_secret() -> None:
    with pytest.raises(ValidationError):
        SourceCatalogCreate(
            source_id=uuid.uuid4(),
            stable_code="mock",
            official_name="Mock",
            source_type="API",
            jurisdiction="DO",
            access_method="API",
            update_frequency="daily",
            configuration={"token": "not-allowed"},
        )


def test_manual_connector_checksum_mime_limit_and_dry_run() -> None:
    result = ManualUploadConnector({"content": b"a,b\n1,2\n"}, max_bytes=20).fetch(dry_run=True)
    assert result.mime_type == "text/csv"
    assert len(result.checksum_sha256) == 64
    assert result.dry_run
    with pytest.raises(ValueError):
        ManualUploadConnector({"content": b"too large"}, max_bytes=2).fetch()


def test_http_conditional_request_and_allowed_headers(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.modules.ingestion.connectors.validate_public_url", lambda url: url)
    seen: list[object] = []

    def transport(request: object, timeout: float) -> tuple[int, dict[str, str], bytes]:
        seen.append(request)
        return 304, {"Authorization": "secret", "ETag": "same"}, b""

    connector = HttpFileConnector(
        {"url": "https://example.test/file", "etag": '"abc"'}, transport=transport
    )
    assert connector.fetch().unchanged
    assert seen


def test_json_connector_rejects_wrong_real_mime(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.modules.ingestion.connectors.validate_public_url", lambda url: url)
    connector = JsonApiConnector(
        {"url": "https://example.test"},
        transport=lambda request, timeout: (200, {"Content-Type": "application/json"}, b"<html>"),
    )
    with pytest.raises(ValueError):
        connector.fetch()


def test_real_mime_ignores_reported_extension() -> None:
    assert detect_mime(b"%PDF-1.7\n") == "application/pdf"
    assert detect_mime(json.dumps([{"a": 1}]).encode()) == "application/json"


def test_csv_parser_delimiter_bom_multiline_and_formula_sanitization() -> None:
    result = CsvParser().parse('\ufeffname;note\nAlice;"line1\nline2"\nBob;=1+1\n'.encode())
    assert len(result.tables[0].rows) == 2
    assert result.tables[0].rows[1].values["note"] == "'=1+1"


def test_csv_duplicate_headers_and_limits() -> None:
    with pytest.raises(ParsingError):
        CsvParser().parse(b"a,a\n1,2\n")
    with pytest.raises(ParsingError):
        CsvParser(max_rows=1).parse(b"a\n1\n2\n")


def test_json_path_depth_and_original_path() -> None:
    result = JsonParser("data").parse(b'{"data":[{"id":1}]}')
    assert result.tables[0].rows[0].source_path == "data[0]"
    with pytest.raises(ParsingError):
        JsonParser(max_depth=1).parse(b'{"a":{"b":{"c":1}}}')


def make_zip(entries: dict[str, bytes], compression: int = zipfile.ZIP_DEFLATED) -> bytes:
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression) as archive:
        for name, content in entries.items():
            archive.writestr(name, content)
    return stream.getvalue()


def test_zip_safe_and_path_traversal() -> None:
    assert ZipParser().inspect(make_zip({"data.csv": b"a\n1\n"}))[0][0] == "data.csv"
    with pytest.raises(UnsafeSourceError):
        safe_archive_name("../escape.csv")
    with pytest.raises(UnsafeSourceError):
        ZipParser().inspect(make_zip({"../escape.csv": b"x"}))


def test_zip_bomb_ratio_and_size() -> None:
    payload = make_zip({"large.txt": b"0" * 10_000})
    with pytest.raises(ParsingError, match="bomb"):
        ZipParser(max_ratio=2).inspect(payload)
    with pytest.raises(ParsingError, match="size"):
        ZipParser(max_uncompressed=10).inspect(payload)


def test_pdf_requires_reliable_controlled_extractor() -> None:
    result = PdfTableParser().parse(b"%PDF-1.7\ncontrolled")
    assert result.needs_review and result.tables == []
    extracted = PdfTableParser(lambda content: [(1, 1, [["a"], ["x"]])]).parse(
        b"%PDF-1.7\ncontrolled"
    )
    assert extracted.tables[0].rows[0].page == 1
    assert extracted.needs_review


def test_normalization_preserves_original_and_sensitive_hash() -> None:
    pipeline = NormalizationPipeline("test-only-salt")
    value = pipeline.apply("  Á  ", "trim")
    assert value.original == "  Á  " and value.normalized == "Á"
    assert len(pipeline.apply("001", "sensitive_hash").normalized) == 64


def test_validation_does_not_infer_missing_values() -> None:
    issues = ValidationPipeline().validate({}, required={"name"})
    assert issues[0].code == "required_missing"


def test_entity_resolver_does_not_merge_ambiguous_matches() -> None:
    matches = EntityResolver().resolve(
        "institution",
        {"normalized_name": "ministerio"},
        [
            {"id": "1", "normalized_name": "ministerio"},
            {"id": "2", "normalized_name": "ministerio"},
        ],
    )
    assert len(matches) == 2
    assert all(match.confidence == Decimal("0.90") for match in matches)


def test_change_detection_records_removed_without_interpreting_it() -> None:
    change = ChangeDetectionService().compare(
        {"1": {"name": "A"}, "2": {"name": "B"}},
        {"1": {"name": "AA"}, "3": {"name": "C"}},
    )
    assert change.added == {"3"}
    assert change.removed == {"2"}
    assert change.modified == {"1"}


def test_canonicalization_requires_human_valid_staging_and_dispatches() -> None:
    events: list[str] = []
    dispatcher = EventDispatcher()
    dispatcher.subscribe(lambda event: events.append(event.name))
    canonicalizer = CanonicalizationService(dispatcher)
    entity_id, evidence_id = uuid.uuid4(), uuid.uuid4()
    result = canonicalizer.canonicalize(
        actor_type="human",
        validation_status="valid",
        domain="budget",
        authorized_service=lambda data, actor: ("unchanged", entity_id),
        evidence_service=lambda: evidence_id,
        normalized_data={"code": "A"},
    )
    assert result.action == "unchanged"
    assert events == ["canonical_data_changed"]
    with pytest.raises(PermissionError):
        canonicalizer.canonicalize(
            actor_type="ai",
            validation_status="valid",
            domain="budget",
            authorized_service=lambda data, actor: ("create", entity_id),
            evidence_service=lambda: evidence_id,
            normalized_data={},
        )


def test_schedule_validation_retry_backoff_and_redaction() -> None:
    assert (
        ScheduleCreate(
            source_catalog_id=uuid.uuid4(), schedule_type="interval", interval_minutes=60
        ).timezone
        == "America/Santo_Domingo"
    )
    with pytest.raises(ValidationError):
        ScheduleCreate(source_catalog_id=uuid.uuid4(), schedule_type="invalid")
    assert retry_delay(20).total_seconds() == 3600
    assert redact_configuration({"token": "x", "url": "ok"}) == {"token": "***", "url": "ok"}
    assert safe_csv_value("@cmd") == "'@cmd"
