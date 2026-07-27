import pytest
from sqlalchemy import create_engine, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from app.db.seed import seed
from app.modules.asset_categories.models import AssetCategory
from app.modules.public_assets.models import PublicAsset
from tests.integration.test_postgresql_guards import migrate

pytestmark = pytest.mark.integration


def _seeded(postgres_url: str) -> tuple[object, PublicAsset, AssetCategory]:
    migrate(postgres_url)
    engine = create_engine(postgres_url)
    with Session(engine) as db:
        seed(db)
        asset = db.scalar(select(PublicAsset).where(PublicAsset.asset_code == "B9-ASSET-LAND-001"))
        category = db.scalar(select(AssetCategory).where(AssetCategory.stable_code == "B9-TECH"))
        assert asset is not None and category is not None
        db.expunge(asset)
        db.expunge(category)
    return engine, asset, category


def test_postgres_rejects_negative_assets_and_ai_actor(postgres_url: str) -> None:
    engine, asset, _ = _seeded(postgres_url)
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            with pytest.raises(DBAPIError, match="ck_asset_values"):
                connection.execute(
                    text("UPDATE public_assets SET current_book_value=-1 WHERE id=:id"),
                    {"id": asset.id},
                )
        finally:
            transaction.rollback()
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            connection.execute(text("SET LOCAL app.actor_type = 'ai'"))
            with pytest.raises(DBAPIError, match="AI actors"):
                connection.execute(
                    text("UPDATE public_assets SET official_name='IA' WHERE id=:id"),
                    {"id": asset.id},
                )
        finally:
            transaction.rollback()


def test_postgres_rejects_hierarchy_cycle_and_incoherent_valuation(
    postgres_url: str,
) -> None:
    engine, asset, category = _seeded(postgres_url)
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            with pytest.raises(DBAPIError, match="cycle"):
                connection.execute(
                    text("UPDATE asset_categories SET parent_id=id WHERE id=:id"),
                    {"id": category.id},
                )
        finally:
            transaction.rollback()
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            with pytest.raises(DBAPIError, match="ck_asset_valuation_formula"):
                connection.execute(
                    text(
                        "UPDATE asset_valuations SET net_book_value=gross_value + 1 "
                        "WHERE asset_id=:id"
                    ),
                    {"id": asset.id},
                )
        finally:
            transaction.rollback()
