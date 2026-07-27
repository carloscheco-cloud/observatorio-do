from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.seed import seed
from app.modules.appointments.models import Appointment
from app.modules.evidence.models import Evidence
from app.modules.institutions.models import Institution, InstitutionEvidence
from app.modules.legal_basis.models import LegalBasis
from app.modules.persons.models import Person
from app.modules.positions.models import Position
from app.modules.sources.models import Source
from app.modules.territories.models import Territory


def test_seed_is_idempotent_and_traceable(db: Session) -> None:
    seed(db)
    seed(db)
    assert db.scalar(select(func.count()).select_from(Territory)) == 5
    assert db.scalar(select(func.count()).select_from(Source)) == 1
    assert db.scalar(select(func.count()).select_from(Evidence)) == 2
    assert db.scalar(select(func.count()).select_from(Institution)) == 1
    assert db.scalar(select(func.count()).select_from(InstitutionEvidence)) == 1
    assert db.scalar(select(func.count()).select_from(Person)) == 1
    assert db.scalar(select(func.count()).select_from(LegalBasis)) == 1
    assert db.scalar(select(func.count()).select_from(Position)) == 1
    assert db.scalar(select(func.count()).select_from(Appointment)) == 1
