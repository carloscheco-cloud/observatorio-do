from __future__ import annotations

import hashlib
import uuid

import pytest
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import DBAPIError

from alembic import command
from tests.integration.test_postgresql_guards import BACKEND_DIR

pytestmark = pytest.mark.integration


def _migration_config(postgres_url: str) -> Config:
    config = Config(BACKEND_DIR / "alembic.ini")
    config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    config.set_main_option("sqlalchemy.url", postgres_url)
    return config


def _institution_id(connection: object) -> uuid.UUID:
    suffix = uuid.uuid4().hex[:20]
    territory_id = uuid.uuid4()
    source_id = uuid.uuid4()
    evidence_id = uuid.uuid4()
    institution_id = uuid.uuid4()
    source_url = f"https://example.gob.do/instituciones/{suffix}"
    content_hash = hashlib.sha256(source_url.encode()).hexdigest()

    connection.execute(  # type: ignore[attr-defined]
        text(
            "INSERT INTO territories (id,name,code,type,parent_id) "
            "VALUES (:id,'República Dominicana',:code,'COUNTRY',NULL)"
        ),
        {"id": territory_id, "code": f"DO-{suffix}"},
    )
    connection.execute(  # type: ignore[attr-defined]
        text(
            "INSERT INTO sources (id,name,url,publisher,is_official) "
            "VALUES (:id,:name,:url,'OED Test',true)"
        ),
        {
            "id": source_id,
            "name": f"Fuente institucional {suffix}",
            "url": source_url,
        },
    )
    connection.execute(  # type: ignore[attr-defined]
        text(
            "INSERT INTO evidence "
            "(id,source_id,title,excerpt,locator,content_hash,metadata) "
            "VALUES (:id,:source,:title,:excerpt,:locator,:hash,'{}')"
        ),
        {
            "id": evidence_id,
            "source": source_id,
            "title": f"Evidencia institucional {suffix}",
            "excerpt": "Registro controlado para validar PE-09.",
            "locator": source_url,
            "hash": content_hash,
        },
    )
    connection.execute(  # type: ignore[attr-defined]
        text(
            "INSERT INTO institutions "
            "(id,name,kind,slug,territory_id,operational_status,coverage_level,status) "
            "VALUES (:id,:name,'ministry',:slug,:territory,'UNKNOWN','NONE','DRAFT')"
        ),
        {
            "id": institution_id,
            "name": f"Ministerio de Prueba {suffix}",
            "slug": f"ministerio-prueba-{suffix}",
            "territory": territory_id,
        },
    )
    connection.execute(  # type: ignore[attr-defined]
        text(
            "INSERT INTO institution_evidence "
            "(id,institution_id,evidence_id,relation) "
            "VALUES (gen_random_uuid(),:institution,:evidence,'supports_existence')"
        ),
        {"institution": institution_id, "evidence": evidence_id},
    )
    return institution_id


def _insert_asset(
    connection: object,
    institution_id: uuid.UUID | None,
    *,
    asset_type: str = "institution_building",
    storage_kind: str = "remote_official",
    source_url: str | None = "https://example.gob.do/asset.jpg",
    approval_status: str = "pending",
    is_primary: bool = False,
    width: int | None = 1200,
    height: int | None = 800,
) -> None:
    connection.execute(  # type: ignore[attr-defined]
        text(
            "INSERT INTO media_assets "
            "(id,institution_id,person_id,asset_type,storage_kind,source_url,public_url,"
            "source_name,approval_status,is_primary,alt_text,width,height) VALUES "
            "(:id,:institution,NULL,:asset_type,:storage_kind,:source_url,:source_url,"
            "'Portal institucional oficial',:status,:primary,'Activo visual de prueba',"
            ":width,:height)"
        ),
        {
            "id": uuid.uuid4(),
            "institution": institution_id,
            "asset_type": asset_type,
            "storage_kind": storage_kind,
            "source_url": source_url,
            "status": approval_status,
            "primary": is_primary,
            "width": width,
            "height": height,
        },
    )


def test_pe09_migration_round_trip(postgres_url: str) -> None:
    config = _migration_config(postgres_url)
    engine = create_engine(postgres_url)

    command.downgrade(config, "0018")
    assert "media_assets" not in inspect(engine).get_table_names()
    with engine.connect() as connection:
        assert connection.scalar(text("SELECT version_num FROM alembic_version")) == "0018"

    command.upgrade(config, "0019")
    assert "media_assets" in inspect(engine).get_table_names()
    with engine.connect() as connection:
        assert connection.scalar(text("SELECT version_num FROM alembic_version")) == "0019"

    engine.dispose()


def test_pe09_owner_source_and_dimension_guards(postgres_url: str) -> None:
    engine = create_engine(postgres_url)
    with engine.begin() as connection:
        institution_id = _institution_id(connection)

    invalid_cases = (
        {"institution_id": None},
        {"institution_id": institution_id, "source_url": None},
        {"institution_id": institution_id, "width": 0},
        {"institution_id": institution_id, "height": -1},
    )
    for overrides in invalid_cases:
        with engine.connect() as connection:
            transaction = connection.begin()
            with pytest.raises(DBAPIError):
                _insert_asset(connection, **overrides)
            transaction.rollback()

    with engine.begin() as connection:
        _insert_asset(
            connection,
            None,
            asset_type="fallback",
            storage_kind="generated_fallback",
            source_url=None,
            width=None,
            height=None,
        )

    engine.dispose()


def test_pe09_allows_many_candidates_but_one_approved_primary(postgres_url: str) -> None:
    engine = create_engine(postgres_url)
    with engine.begin() as connection:
        institution_id = _institution_id(connection)
        _insert_asset(
            connection,
            institution_id,
            source_url="https://example.gob.do/pending.jpg",
            approval_status="pending",
            is_primary=True,
        )
        _insert_asset(
            connection,
            institution_id,
            source_url="https://example.gob.do/approved-1.jpg",
            approval_status="approved",
            is_primary=True,
        )
        _insert_asset(
            connection,
            institution_id,
            source_url="https://example.gob.do/secondary.jpg",
            approval_status="approved",
            is_primary=False,
        )

    with engine.connect() as connection:
        transaction = connection.begin()
        with pytest.raises(DBAPIError):
            _insert_asset(
                connection,
                institution_id,
                source_url="https://example.gob.do/approved-2.jpg",
                approval_status="approved",
                is_primary=True,
            )
        transaction.rollback()

    engine.dispose()
