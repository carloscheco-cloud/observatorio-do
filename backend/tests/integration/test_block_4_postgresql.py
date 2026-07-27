import uuid
from datetime import date

import pytest
from sqlalchemy import create_engine, select, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from app.db.seed import seed
from app.modules.institutions.models import Institution
from app.modules.organizational_units.models import OrganizationalUnit, UnitStatus, UnitType
from app.modules.positions.models import Position
from tests.integration.test_postgresql_guards import migrate

pytestmark = pytest.mark.integration


def _seeded(postgres_url: str) -> tuple[Engine, uuid.UUID, uuid.UUID]:
    migrate(postgres_url)
    engine = create_engine(postgres_url)
    with Session(engine) as db:
        seed(db)
        root = db.scalar(
            select(OrganizationalUnit).where(OrganizationalUnit.stable_code == "CONTROL-B4-ROOT")
        )
        division = db.scalar(
            select(OrganizationalUnit).where(OrganizationalUnit.stable_code == "CONTROL-B4-DIV-NOM")
        )
        assert root and division
        return engine, root.id, division.id


def test_postgres_rejects_hierarchy_cycles(postgres_url: str) -> None:
    engine, root_id, division_id = _seeded(postgres_url)
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            with pytest.raises(DBAPIError, match="cycle"):
                connection.execute(
                    text(
                        "UPDATE organizational_units SET parent_unit_id=:division, "
                        "hierarchy_level=4 WHERE id=:root"
                    ),
                    {"division": division_id, "root": root_id},
                )
        finally:
            transaction.rollback()


def test_postgres_rejects_canonical_unit_without_evidence(postgres_url: str) -> None:
    engine, root_id, _ = _seeded(postgres_url)
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            connection.execute(
                text("DELETE FROM organizational_unit_evidence WHERE unit_id=:unit"),
                {"unit": root_id},
            )
            with pytest.raises(DBAPIError, match="requires legal basis, evidence and source"):
                connection.execute(text("SET CONSTRAINTS ALL IMMEDIATE"))
        finally:
            transaction.rollback()


def test_postgres_rejects_ai_organizational_write(postgres_url: str) -> None:
    engine, _, _ = _seeded(postgres_url)
    with engine.connect() as connection:
        transaction = connection.begin()
        institution_id = connection.scalar(text("SELECT id FROM institutions LIMIT 1"))
        try:
            connection.execute(text("SET LOCAL app.actor_type = 'ai'"))
            with pytest.raises(DBAPIError, match="AI actors"):
                connection.execute(
                    text(
                        "INSERT INTO organizational_units "
                        "(id,institution_id,official_name,normalized_name,stable_code,"
                        "unit_type,hierarchy_level,status,valid_from,metadata) VALUES "
                        "(:id,:institution,'IA','ia',:code,'OTHER',0,'DRAFT',CURRENT_DATE,'{}')"
                    ),
                    {
                        "id": uuid.uuid4(),
                        "institution": institution_id,
                        "code": f"AI-{uuid.uuid4()}",
                    },
                )
        finally:
            transaction.rollback()


def test_postgres_rejects_invalid_dates(postgres_url: str) -> None:
    engine, root_id, _ = _seeded(postgres_url)
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            with pytest.raises(DBAPIError, match="ck_unit_dates"):
                connection.execute(
                    text("UPDATE organizational_units SET valid_to=valid_from - 1 WHERE id=:unit"),
                    {"unit": root_id},
                )
        finally:
            transaction.rollback()


def test_postgres_rejects_position_unit_from_other_institution(postgres_url: str) -> None:
    engine, _, _ = _seeded(postgres_url)
    with Session(engine) as db:
        institution = db.scalar(select(Institution))
        position = db.scalar(select(Position).where(Position.code == "CONTROL-B4-DIRECTOR-ADM"))
        assert institution and position
        other = Institution(
            name=f"Institución alterna {uuid.uuid4()}",
            kind="controlled_test",
            territory_id=institution.territory_id,
        )
        db.add(other)
        db.flush()
        unit = OrganizationalUnit(
            institution_id=other.id,
            official_name="Unidad alterna",
            normalized_name="unidad alterna",
            stable_code=f"ALT-{uuid.uuid4()}",
            unit_type=UnitType.OTHER,
            hierarchy_level=0,
            status=UnitStatus.DRAFT,
            valid_from=date.today(),
        )
        db.add(unit)
        db.flush()
        with pytest.raises(DBAPIError, match="same institution"):
            db.execute(
                text("UPDATE positions SET organizational_unit_id=:unit WHERE id=:position"),
                {"unit": unit.id, "position": position.id},
            )
        db.rollback()
