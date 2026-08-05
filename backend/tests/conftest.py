import os
import uuid
from collections.abc import Generator
from pathlib import Path

import pytest
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from alembic import command
from app.db.base import Base
from app.modules import models  # noqa: F401
from tests.postgres import EXPECTED_SCHEMA_REVISION, POSTGRES_ADMIN_ENV

BACKEND_DIR = Path(__file__).resolve().parents[1]


def _integration_admin_url() -> URL:
    configured = os.getenv(POSTGRES_ADMIN_ENV)
    fallback = False
    if not configured:
        configured = os.getenv("DATABASE_URL")
        fallback = bool(configured)
    if not configured:
        message = (
            f"{POSTGRES_ADMIN_ENV} is required for PostgreSQL integration tests; "
            "DATABASE_URL is accepted as a compatible fallback"
        )
        if os.getenv("CI"):
            pytest.fail(message, pytrace=False)
        pytest.skip(message)
    try:
        parsed = make_url(configured)
    except Exception:
        pytest.fail(
            f"{POSTGRES_ADMIN_ENV} is not a valid SQLAlchemy URL; credentials were not shown",
            pytrace=False,
        )
    if parsed.get_backend_name() != "postgresql":
        pytest.fail(
            f"{POSTGRES_ADMIN_ENV} must use PostgreSQL, not {parsed.get_backend_name()}",
            pytrace=False,
        )
    if parsed.drivername != "postgresql+psycopg":
        pytest.fail(
            f"{POSTGRES_ADMIN_ENV} must use the postgresql+psycopg driver",
            pytrace=False,
        )
    return parsed.set(database="postgres") if fallback else parsed


def _safe_connection_failure(error: OperationalError) -> str:
    message = str(error.orig).casefold()
    if "password authentication failed" in message or "autentificaci" in message:
        return "PostgreSQL authentication failed"
    if "does not exist" in message or "no existe" in message:
        return "PostgreSQL administrative database does not exist"
    if "connection refused" in message or "conexión" in message or "conexion" in message:
        return "PostgreSQL host or port is not reachable"
    return "PostgreSQL administrative connection failed"


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
    admin_url = _integration_admin_url()
    template_name = f"oed_template_{uuid.uuid4().hex}"
    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    try:
        with admin_engine.connect() as connection:
            can_create = connection.scalar(
                text("SELECT rolcreatedb OR rolsuper FROM pg_roles WHERE rolname=current_user")
            )
            if not can_create:
                pytest.fail(
                    "PostgreSQL integration user requires CREATEDB or superuser permission",
                    pytrace=False,
                )
            connection.execute(text(f'CREATE DATABASE "{template_name}"'))
    except OperationalError as error:
        pytest.fail(_safe_connection_failure(error), pytrace=False)
    template_url = admin_url.set(database=template_name)
    migration = Config(BACKEND_DIR / "alembic.ini")
    migration.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    migration.set_main_option("sqlalchemy.url", template_url.render_as_string(hide_password=False))
    previous_url = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = template_url.render_as_string(hide_password=False)
    try:
        command.upgrade(migration, "head")
        verification_engine = create_engine(template_url)
        try:
            with verification_engine.connect() as connection:
                revision = connection.scalar(text("SELECT version_num FROM alembic_version"))
            if revision != EXPECTED_SCHEMA_REVISION:
                pytest.fail(
                    "PostgreSQL template schema revision is not the expected test revision",
                    pytrace=False,
                )
        finally:
            verification_engine.dispose()
    finally:
        if previous_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = previous_url
    try:
        yield admin_url, template_name
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
    admin_url, template_name = migrated_postgres_template
    database_name = f"oed_test_{uuid.uuid4().hex}"
    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as connection:
        connection.execute(text(f'CREATE DATABASE "{database_name}" TEMPLATE "{template_name}"'))
    test_url = admin_url.set(database=database_name)
    rendered_test_url = test_url.render_as_string(hide_password=False)
    previous_url = os.environ.get("DATABASE_URL")
    previous_schema_version = os.environ.get("OED_TEST_SCHEMA_VERSION")
    os.environ["DATABASE_URL"] = rendered_test_url
    os.environ["OED_TEST_SCHEMA_VERSION"] = EXPECTED_SCHEMA_REVISION
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
