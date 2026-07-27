"""Central model import used only for SQLAlchemy metadata discovery."""

from app.modules.evidence.models import Evidence
from app.modules.institutions.models import Institution, InstitutionEvidence
from app.modules.sources.models import Source
from app.modules.territories.models import Territory

__all__ = ["Evidence", "Institution", "InstitutionEvidence", "Source", "Territory"]
