from __future__ import annotations

import hashlib
import json
import time
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Protocol

from app.modules.ingestion.security import redact_configuration, validate_public_url


class Transport(Protocol):
    def __call__(
        self, request: urllib.request.Request, timeout: float
    ) -> tuple[int, dict[str, str], bytes]: ...


@dataclass(frozen=True)
class ConnectorResult:
    content: bytes
    checksum_sha256: str
    mime_type: str
    status_code: int = 200
    headers: dict[str, str] = field(default_factory=dict)
    unchanged: bool = False
    dry_run: bool = False


def detect_mime(content: bytes) -> str:
    stripped = content.lstrip()
    if content.startswith(b"PK\x03\x04"):
        return "application/zip"
    if content.startswith(b"%PDF-"):
        return "application/pdf"
    if stripped.startswith((b"{", b"[")):
        try:
            json.loads(content)
            return "application/json"
        except (ValueError, UnicodeDecodeError):
            pass
    if b"\n" in content and (b"," in content.splitlines()[0] or b";" in content.splitlines()[0]):
        return "text/csv"
    return "application/octet-stream"


class BaseConnector(ABC):
    allowed_headers = {"content-type", "content-length", "etag", "last-modified", "retry-after"}

    def __init__(
        self,
        config: dict[str, object],
        *,
        timeout: float = 20,
        max_bytes: int = 25_000_000,
        retries: int = 2,
    ) -> None:
        self.config = config
        self.timeout = timeout
        self.max_bytes = max_bytes
        self.retries = retries
        self.validate_configuration()

    def validate_configuration(self) -> None:
        if any(k.lower() in {"password", "token", "secret", "api_key"} for k in self.config):
            raise ValueError("connector configuration may only contain environment references")

    @abstractmethod
    def fetch(self, *, dry_run: bool = False) -> ConnectorResult: ...

    def test_availability(self) -> bool:
        return self.fetch(dry_run=True).status_code < 400

    @property
    def safe_configuration(self) -> dict[str, object]:
        return redact_configuration(self.config)


def _stdlib_transport(
    request: urllib.request.Request, timeout: float
) -> tuple[int, dict[str, str], bytes]:
    with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
        return response.status, dict(response.headers.items()), response.read()


class HttpFileConnector(BaseConnector):
    def __init__(self, *args: object, transport: Transport = _stdlib_transport, **kwargs: object):
        self.transport = transport
        super().__init__(*args, **kwargs)  # type: ignore[arg-type]

    def validate_configuration(self) -> None:
        super().validate_configuration()
        url = self.config.get("url")
        if not isinstance(url, str):
            raise ValueError("url is required")
        validate_public_url(url)

    def fetch(self, *, dry_run: bool = False) -> ConnectorResult:
        headers = {"User-Agent": "ObservatorioDO-Ingestion/1.0"}
        for source, target in (("etag", "If-None-Match"), ("last_modified", "If-Modified-Since")):
            value = self.config.get(source)
            if isinstance(value, str):
                headers[target] = value
        method = "HEAD" if dry_run else "GET"
        request = urllib.request.Request(str(self.config["url"]), headers=headers, method=method)
        for attempt in range(self.retries + 1):
            try:
                status, response_headers, content = self.transport(request, self.timeout)
                if status == 304:
                    return ConnectorResult(
                        b"", hashlib.sha256(b"").hexdigest(), "", status, unchanged=True
                    )
                if len(content) > self.max_bytes:
                    raise ValueError("download exceeds configured maximum")
                permitted = {
                    k.lower(): v
                    for k, v in response_headers.items()
                    if k.lower() in self.allowed_headers
                }
                return ConnectorResult(
                    content,
                    hashlib.sha256(content).hexdigest(),
                    detect_mime(content),
                    status,
                    permitted,
                    dry_run=dry_run,
                )
            except (TimeoutError, urllib.error.URLError):
                if attempt >= self.retries:
                    raise
                time.sleep(min(0.1 * (2**attempt), 1))
        raise RuntimeError("unreachable")


class JsonApiConnector(HttpFileConnector):
    def fetch(self, *, dry_run: bool = False) -> ConnectorResult:
        result = super().fetch(dry_run=dry_run)
        if result.content and result.mime_type != "application/json":
            raise ValueError("API response is not valid JSON")
        return result


class CsvConnector(HttpFileConnector):
    pass


class XlsxConnector(HttpFileConnector):
    pass


class PdfTableConnector(HttpFileConnector):
    pass


class ManualUploadConnector(BaseConnector):
    def fetch(self, *, dry_run: bool = False) -> ConnectorResult:
        value = self.config.get("content")
        content = value if isinstance(value, bytes) else b""
        if len(content) > self.max_bytes:
            raise ValueError("upload exceeds configured maximum")
        return ConnectorResult(
            content, hashlib.sha256(content).hexdigest(), detect_mime(content), dry_run=dry_run
        )


class MockConnector(ManualUploadConnector):
    pass
