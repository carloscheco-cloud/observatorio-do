from fastapi import APIRouter

from app.modules.appointments.router import router as appointments_router
from app.modules.budget.router import router as budget_router
from app.modules.employment_relationships.router import router as employment_router
from app.modules.evidence.router import router as evidence_router
from app.modules.institutions.router import router as institutions_router
from app.modules.legal_basis.router import router as legal_basis_router
from app.modules.organizational_units.router import router as organizational_units_router
from app.modules.payroll_entries.router import router as payroll_entries_router
from app.modules.payroll_findings.router import router as payroll_findings_router
from app.modules.payroll_periods.router import router as payroll_periods_router
from app.modules.persons.router import router as persons_router
from app.modules.positions.router import router as positions_router
from app.modules.sources.router import router as sources_router
from app.modules.territories.router import router as territories_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(territories_router)
api_router.include_router(sources_router)
api_router.include_router(evidence_router)
api_router.include_router(institutions_router)
api_router.include_router(persons_router)
api_router.include_router(positions_router)
api_router.include_router(appointments_router)
api_router.include_router(legal_basis_router)
api_router.include_router(organizational_units_router)
api_router.include_router(employment_router)
api_router.include_router(payroll_periods_router)
api_router.include_router(payroll_entries_router)
api_router.include_router(payroll_findings_router)
api_router.include_router(budget_router)
