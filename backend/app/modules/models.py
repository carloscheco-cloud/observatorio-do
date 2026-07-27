"""Central model import used only for SQLAlchemy metadata discovery."""

from app.modules.appointments.models import Appointment
from app.modules.evidence.models import Evidence
from app.modules.institutions.models import Institution, InstitutionEvidence
from app.modules.legal_basis.models import LegalBasis
from app.modules.persons.models import Person
from app.modules.positions.models import Position
from app.modules.sources.models import Source
from app.modules.territories.models import Territory

__all__ = [
    "Appointment",
    "Evidence",
    "Institution",
    "InstitutionEvidence",
    "LegalBasis",
    "Person",
    "Position",
    "Source",
    "Territory",
]
