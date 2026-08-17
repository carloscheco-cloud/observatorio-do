from functools import lru_cache
from typing import Self

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_debug: bool = False
    database_url: str = "postgresql+psycopg://observatorio:observatorio@localhost:5432/observatorio"
    database_pool_size: int = 5
    database_max_overflow: int = 5
    database_pool_timeout_seconds: int = 30
    artifact_storage_backend: str = "local"
    artifact_storage_path: str = ".data/artifacts"
    s3_endpoint_url: str | None = None
    s3_region: str = "us-east-1"
    s3_bucket: str | None = None
    s3_access_key_id: str | None = None
    s3_secret_access_key: str | None = None
    ingestion_max_download_bytes: int = 25_000_000
    ingestion_http_timeout_seconds: int = 20
    ingestion_scheduler_enabled: bool = False
    ingestion_timezone: str = "America/Santo_Domingo"
    autonomy_mode_enabled: bool = False
    autonomy_target_basic_coverage: float = 0.80
    public_api_page_size_max: int = 100
    public_api_cache_seconds: int = 60
    public_api_rate_limit_per_minute: int = 120
    cors_origins: str = "http://localhost:3000"
    trusted_hosts: str = "localhost,127.0.0.1,testserver"
    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", validate_default=True, hide_input_in_errors=True
    )

    @field_validator("database_url")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if value.startswith("postgres://"):
            value = "postgresql+psycopg://" + value.removeprefix("postgres://")
        elif value.startswith("postgresql://"):
            value = "postgresql+psycopg://" + value.removeprefix("postgresql://")
        if not value.startswith("postgresql+psycopg://"):
            raise ValueError("DATABASE_URL must use PostgreSQL with the psycopg driver")
        return value

    @field_validator("cors_origins", "trusted_hosts")
    @classmethod
    def require_nonempty_list(cls, value: str) -> str:
        if not [item.strip() for item in value.split(",") if item.strip()]:
            raise ValueError("must contain at least one explicit value")
        return value

    @field_validator("autonomy_target_basic_coverage")
    @classmethod
    def validate_autonomy_target(cls, value: float) -> float:
        if not 0 < value <= 1:
            raise ValueError("AUTONOMY_TARGET_BASIC_COVERAGE must be greater than 0 and at most 1")
        return value

    @model_validator(mode="after")
    def validate_environment(self) -> Self:
        if self.ingestion_scheduler_enabled:
            raise ValueError("INGESTION_SCHEDULER_ENABLED cannot start inside the API")
        if self.artifact_storage_backend not in {"local", "s3"}:
            raise ValueError("ARTIFACT_STORAGE_BACKEND must be 'local' or 's3'")
        if self.artifact_storage_backend == "s3" and not all(
            (self.s3_endpoint_url, self.s3_bucket, self.s3_access_key_id, self.s3_secret_access_key)
        ):
            raise ValueError("S3 storage requires endpoint, bucket, access key, and secret key")
        if self.app_env.casefold() == "production":
            forbidden = ("localhost", "127.0.0.1", "observatorio:observatorio@")
            if any(item in self.database_url.casefold() for item in forbidden):
                raise ValueError(
                    "production DATABASE_URL cannot use localhost or default credentials"
                )
            if any(
                item in self.cors_origins.casefold() for item in ("localhost", "127.0.0.1", "*")
            ):
                raise ValueError("production CORS_ORIGINS must contain explicit public origins")
            if any(
                item in self.trusted_hosts.casefold() for item in ("localhost", "127.0.0.1", "*")
            ):
                raise ValueError("production TRUSTED_HOSTS must contain explicit public hosts")
            if self.artifact_storage_backend != "s3":
                raise ValueError("production requires ARTIFACT_STORAGE_BACKEND=s3")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
