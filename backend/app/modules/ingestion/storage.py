from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
from pathlib import Path

import boto3  # type: ignore[import-untyped]

from app.core.config import Settings


class ArtifactStorage(ABC):
    @abstractmethod
    def put(self, content: bytes, *, suffix: str = "") -> str: ...

    @abstractmethod
    def get(self, storage_key: str) -> bytes: ...


class LocalArtifactStorage(ArtifactStorage):
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def put(self, content: bytes, *, suffix: str = "") -> str:
        safe_suffix = suffix if suffix.startswith(".") and suffix[1:].isalnum() else ""
        digest = hashlib.sha256(content).hexdigest()
        key = f"{digest[:2]}/{digest}{safe_suffix}"
        destination = (self.root / key).resolve()
        if not destination.is_relative_to(self.root):
            raise ValueError("invalid storage key")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
        return key

    def get(self, storage_key: str) -> bytes:
        path = (self.root / storage_key).resolve()
        if not path.is_relative_to(self.root):
            raise ValueError("invalid storage key")
        return path.read_bytes()


class S3CompatibleArtifactStorage(ArtifactStorage):
    """Adapter boundary; inject an S3 client without coupling domain code to an SDK."""

    def __init__(self, client: object, bucket: str) -> None:
        self.client = client
        self.bucket = bucket

    def put(self, content: bytes, *, suffix: str = "") -> str:
        key = f"artifacts/{hashlib.sha256(content).hexdigest()}{suffix}"
        self.client.put_object(Bucket=self.bucket, Key=key, Body=content)  # type: ignore[attr-defined]
        return key

    def get(self, storage_key: str) -> bytes:
        result = self.client.get_object(Bucket=self.bucket, Key=storage_key)  # type: ignore[attr-defined]
        content = result["Body"].read()
        if not isinstance(content, bytes):
            raise TypeError("storage client returned non-bytes content")
        return content


def build_artifact_storage(settings: Settings) -> ArtifactStorage:
    if settings.artifact_storage_backend == "local":
        return LocalArtifactStorage(Path(settings.artifact_storage_path))
    client = boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        region_name=settings.s3_region,
        aws_access_key_id=settings.s3_access_key_id,
        aws_secret_access_key=settings.s3_secret_access_key,
    )
    if settings.s3_bucket is None:
        raise ValueError("S3_BUCKET is required")
    return S3CompatibleArtifactStorage(client, settings.s3_bucket)
