from __future__ import annotations

import ipaddress
import socket
from pathlib import PurePosixPath
from urllib.parse import urlparse


class UnsafeSourceError(ValueError):
    pass


def validate_public_url(url: str, resolver: object = socket.getaddrinfo) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise UnsafeSourceError("only HTTP/HTTPS sources are allowed")
    hostname = parsed.hostname.rstrip(".").lower()
    if hostname in {"localhost", "metadata.google.internal"} or hostname.endswith(".localhost"):
        raise UnsafeSourceError("local and metadata hosts are blocked")
    if hostname == "169.254.169.254":
        raise UnsafeSourceError("cloud metadata endpoint is blocked")
    try:
        addresses = resolver(hostname, parsed.port or 443, type=socket.SOCK_STREAM)  # type: ignore[operator]
    except OSError as exc:
        raise UnsafeSourceError("source host cannot be resolved") from exc
    for result in addresses:
        address = ipaddress.ip_address(result[4][0])
        if not address.is_global:
            raise UnsafeSourceError(
                "private, loopback, link-local, and reserved networks are blocked"
            )
    return url


def safe_archive_name(name: str) -> str:
    path = PurePosixPath(name.replace("\\", "/"))
    if path.is_absolute() or ".." in path.parts or not path.name:
        raise UnsafeSourceError("archive path traversal detected")
    return path.as_posix()


def redact_configuration(config: dict[str, object]) -> dict[str, object]:
    sensitive = {"authorization", "token", "password", "secret", "api_key", "cookie"}
    return {key: "***" if key.lower() in sensitive else value for key, value in config.items()}


def safe_csv_value(value: str) -> str:
    return "'" + value if value.lstrip().startswith(("=", "+", "-", "@")) else value
