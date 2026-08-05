import os
import uuid
from collections.abc import Generator
from pathlib import Path

import pytest
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from alembic import command
from app.db.base import Base
from app.modules import models  # noqa: F401

BACKEND_DIR = Path(__file__).resolve().parents[1]


@pytest.fixture
def db() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="session")
def migrated_postgres_template() -> Generator[tuple[URL, str], None, None]:
    configured_url = os.getenv("DATABASE_URL")
    if not configured_url or not configured_url.startswith("postgresql"):
        pytest.skip("DATABASE_URL must point to PostgreSQL")
    parsed = make_url(configured_url)
    template_name = f"oed_template_{uuid.uuid4().hex}"
    admin_url = parsed.set(database="postgres")
    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as connection:
        connection.execute(text(f'CREATE DATABASE "{template_name}"'))
    template_url = parsed.set(database=template_name)
    migration = Config(BACKEND_DIR / "alembic.ini")
    migration.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    migration.set_main_option("sqlalchemy.url", template_url.render_as_string(hide_password=False))
    previous_url = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = template_url.render_as_string(hide_password=False)
    try:
        command.upgrade(migration, "head")
    finally:
        if previous_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = previous_url
    try:
        yield parsed, template_name
    finally:
        with admin_engine.connect() as connection:
            connection.execute(
                text(
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                    "WHERE datname=:database AND pid <> pg_backend_pid()"
                ),
                {"database": template_name},
            )
            connection.execute(text(f'DROP DATABASE "{template_name}"'))
        admin_engine.dispose()


@pytest.fixture
def postgres_url(
    migrated_postgres_template: tuple[URL, str],
) -> Generator[str, None, None]:
    parsed, template_name = migrated_postgres_template
    database_name = f"oed_test_{uuid.uuid4().hex}"
    admin_url = parsed.set(database="postgres")
    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as connection:
        connection.execute(text(f'CREATE DATABASE "{database_name}" TEMPLATE "{template_name}"'))
    test_url = parsed.set(database=database_name)
    rendered_test_url = test_url.render_as_string(hide_password=False)
    previous_url = os.environ.get("DATABASE_URL")
    previous_schema_version = os.environ.get("OED_TEST_SCHEMA_VERSION")
    os.environ["DATABASE_URL"] = rendered_test_url
    os.environ["OED_TEST_SCHEMA_VERSION"] = "0018"
    try:
        yield rendered_test_url
    finally:
        if previous_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = previous_url
        if previous_schema_version is None:
            os.environ.pop("OED_TEST_SCHEMA_VERSION", None)
        else:
            os.environ["OED_TEST_SCHEMA_VERSION"] = previous_schema_version
        with admin_engine.connect() as connection:
            connection.execute(
                text(
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                    "WHERE datname=:database AND pid <> pg_backend_pid()"
                ),
                {"database": database_name},
            )
            connection.execute(text(f'DROP DATABASE "{database_name}"'))
        admin_engine.dispose()
