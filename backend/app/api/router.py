from fastapi import APIRouter

from app.modules.evidence.router import router as evidence_router
from app.modules.institutions.router import router as institutions_router
from app.modules.sources.router import router as sources_router
from app.modules.territories.router import router as territories_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(territories_router)
api_router.include_router(sources_router)
api_router.include_router(evidence_router)
api_router.include_router(institutions_router)
