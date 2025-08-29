from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.startup import validate_environment
from app.db.session import engine
from app.api.routes import auth, purposes, categories, supernets, subnets, vlans
from app.api.routes import devices, racks, ip_assignments, audits, search, export

validate_environment()

def _parse_origins(origins_str: str) -> list[str]:
    if not origins_str:
        return []
    origins = [o.strip() for o in origins_str.replace(" ", "").split(",") if o.strip()]
    
    for origin in origins:
        if origin == "*":
            raise ValueError("Wildcard origins not allowed with credentials")
        if not origin.startswith(("http://", "https://")):
            raise ValueError(f"Invalid origin format: {origin}")
    
    return origins


app = FastAPI(title="IPAM")

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cors_kwargs = {
    "allow_credentials": True,
    "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Explicit methods
    "allow_headers": ["Authorization", "Content-Type", "Accept"],   # Explicit headers
    "allow_origins": [],  # No default - must be explicitly set
}

origin_list = _parse_origins(settings.CORS_ORIGINS)
if origin_list:
    cors_kwargs["allow_origins"] = origin_list
    logger.info(f"CORS origins configured: {origin_list}")

if settings.CORS_ORIGIN_REGEX:
    try:
        import re
        re.compile(settings.CORS_ORIGIN_REGEX)
        cors_kwargs["allow_origin_regex"] = settings.CORS_ORIGIN_REGEX
        logger.info(f"CORS origin regex configured: {settings.CORS_ORIGIN_REGEX}")
    except re.error as e:
        raise ValueError(f"Invalid CORS origin regex: {e}")

if not origin_list and not settings.CORS_ORIGIN_REGEX:
    cors_kwargs["allow_origins"] = ["http://localhost:5173", "http://localhost:5174"]
    logger.info("Using default localhost CORS origins for development")

app.add_middleware(CORSMiddleware, **cors_kwargs)

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    if settings.ENV == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    return response

logger.info("CORS middleware configured successfully")


@app.get("/", include_in_schema=False)
async def root():
    return {"service": "ipam-api", "docs": "/docs", "health": "/healthz"}


@app.get("/healthz")
async def healthz():
    try:
        async with AsyncSession(engine) as session:
            await session.execute(text("SELECT 1"))
        
        return {"status": "ok", "database": "connected"}
    
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        
        if settings.ENV == "development":
            return {
                "status": "degraded",
                "database": "disconnected",
                "error": str(e)[:100]  # Truncate error message
            }
        else:
            return {
                "status": "degraded",
                "database": "disconnected"
            }


app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(purposes.router, prefix="/api/purposes", tags=["purposes"])
app.include_router(categories.router, prefix="/api/categories", tags=["categories"])
app.include_router(supernets.router, prefix="/api/supernets", tags=["supernets"])
app.include_router(subnets.router, prefix="/api/subnets", tags=["subnets"])
app.include_router(vlans.router, prefix="/api/vlans", tags=["vlans"])
app.include_router(devices.router, prefix="/api/devices", tags=["devices"])
app.include_router(racks.router, prefix="/api/racks", tags=["racks"])
app.include_router(ip_assignments.router, prefix="/api/ip-assignments", tags=["ip-assignments"])
app.include_router(audits.router, prefix="/api/audits", tags=["audits"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(export.router, prefix="/api/export", tags=["export"])

from app.api.routes import health
app.include_router(health.router, prefix="/api", tags=["health"])
