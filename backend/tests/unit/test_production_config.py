from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def production_settings(**overrides: object) -> Settings:
    values: dict[str, object] = {
        "app_env": "production",
        "database_url": "postgresql://user:password@db.example.com:5432/oed?sslmode=require",
        "cors_origins": "https://observatorio.example",
        "trusted_hosts": "api.observatorio.example",
        "artifact_storage_backend": "s3",
        "s3_endpoint_url": "https://s3.example",
        "s3_bucket": "artifacts",
        "s3_access_key_id": "access",
        "s3_secret_access_key": "secret",
    }
    values.update(overrides)
    return Settings(**values)


def test_supabase_style_url_is_normalized_and_preserves_ssl() -> None:
    configured = production_settings()
    assert configured.database_url.startswith("postgresql+psycopg://")
    assert configured.database_url.endswith("?sslmode=require")


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("database_url", "postgresql://observatorio:observatorio@localhost/oed"),
        ("cors_origins", "*"),
        ("trusted_hosts", "*"),
        ("artifact_storage_backend", "local"),
    ],
)
def test_production_rejects_unsafe_defaults(field: str, value: str) -> None:
    with pytest.raises(ValidationError):
        production_settings(**{field: value})


def test_api_cannot_enable_ingestion_scheduler() -> None:
    with pytest.raises(ValidationError):
        production_settings(ingestion_scheduler_enabled=True)
