import hashlib
import time
import uuid
from collections import defaultdict, deque
from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session
from starlette.responses import Response

from app.api.router import api_router
from app.core.config import settings
from app.db.session import get_db

app = FastAPI(
    title="API del Observatorio del Estado Dominicano",
    description="API pública independiente. Sólo publica datos revisados y campos autorizados.",
    version="1.0.0",
    contact={"name": "Observatorio del Estado Dominicano"},
    terms_of_service="https://observatorio.example/terminos",
)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[item.strip() for item in settings.trusted_hosts.split(",")],
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[item.strip() for item in settings.cors_origins.split(",")],
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["Accept", "Content-Type", "If-None-Match", "X-Request-ID"],
)
app.include_router(api_router)
DatabaseSession = Annotated[Session, Depends(get_db)]
_requests: defaultdict[str, deque[float]] = defaultdict(deque)


@app.middleware("http")
async def public_security(request: Request, call_next: object) -> Response:
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))[:80]
    if request.url.path.startswith(("/api/v1/public/", "/api/v1/executive/")):
        now = time.monotonic()
        key = request.client.host if request.client else "unknown"
        bucket = _requests[key]
        while bucket and bucket[0] < now - 60:
            bucket.popleft()
        if len(bucket) >= settings.public_api_rate_limit_per_minute:
            return JSONResponse(
                status_code=429,
                content={
                    "code": "rate_limited",
                    "message": "Demasiadas solicitudes.",
                    "details": {},
                    "request_id": request_id,
                    "timestamp": datetime.now(UTC).isoformat(),
                },
                headers={"Retry-After": "60", "X-Request-ID": request_id},
            )
        bucket.append(now)
    response: Response = await call_next(request)  # type: ignore[operator]
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if request.method == "GET" and request.url.path.startswith(
        ("/api/v1/public/", "/api/v1/executive/")
    ):
        cache_identity = f"{request.url.path}?{request.url.query}".encode()
        etag = f'"{hashlib.sha256(cache_identity).hexdigest()}"'
        response.headers["ETag"] = etag
        response.headers["Cache-Control"] = "public, max-age=60, stale-while-revalidate=300"
        if request.headers.get("if-none-match") == etag:
            return JSONResponse(status_code=304, content=None, headers=dict(response.headers))
    return response


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))[:80]
    details = [
        {"field": ".".join(str(part) for part in item["loc"]), "message": item["msg"]}
        for item in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={
            "code": "validation_error",
            "message": "Los parámetros no son válidos.",
            "details": {"errors": details},
            "request_id": request_id,
            "timestamp": datetime.now(UTC).isoformat(),
        },
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/db")
def health_db(db: DatabaseSession) -> dict[str, str]:
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "reachable"}
