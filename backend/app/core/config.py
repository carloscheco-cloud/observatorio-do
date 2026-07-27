from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_debug: bool = False
    database_url: str = "postgresql+psycopg://observatorio:observatorio@localhost:5432/observatorio"
    artifact_storage_path: str = ".data/artifacts"
    ingestion_max_download_bytes: int = 25_000_000
    ingestion_http_timeout_seconds: int = 20
    ingestion_scheduler_enabled: bool = False
    ingestion_timezone: str = "America/Santo_Domingo"
    public_api_page_size_max: int = 100
    public_api_cache_seconds: int = 60
    public_api_rate_limit_per_minute: int = 120
    cors_origins: str = "http://localhost:3000"
    trusted_hosts: str = "localhost,127.0.0.1,testserver"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
