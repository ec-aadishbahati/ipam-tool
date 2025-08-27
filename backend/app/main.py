from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.startup import validate_environment
from app.db.session import engine
from app.api.routes import auth, purposes, supernets, subnets, vlans
from app.api.routes import devices, ip_assignments, audits, search

validate_environment()

def _parse_origins(origins_str: str) -> list[str]:
    if not origins_str:
        return []
    return [o.strip() for o in origins_str.replace(" ", "").split(",") if o.strip()]


app = FastAPI(title="IPAM")

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cors_kwargs = {
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
    "allow_origins": ["*"],
}
origin_list = _parse_origins(settings.CORS_ORIGINS)
if origin_list:
    cors_kwargs["allow_origins"] = origin_list
    logger.info(f"CORS origins configured: {origin_list}")
if settings.CORS_ORIGIN_REGEX:
    cors_kwargs["allow_origin_regex"] = settings.CORS_ORIGIN_REGEX
    logger.info(f"CORS origin regex configured: {settings.CORS_ORIGIN_REGEX}")

if (
    cors_kwargs["allow_credentials"]
    and not origin_list
    and not settings.CORS_ORIGIN_REGEX
):
    raise RuntimeError(
        "CORS_ORIGINS must be defined when allow_credentials=True"
    )

app.add_middleware(CORSMiddleware, **cors_kwargs)
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
        import traceback
        return {
            "status": "degraded", 
            "database": "disconnected", 
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc()
        }


app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(purposes.router, prefix="/api/purposes", tags=["purposes"])
app.include_router(supernets.router, prefix="/api/supernets", tags=["supernets"])
app.include_router(subnets.router, prefix="/api/subnets", tags=["subnets"])
app.include_router(vlans.router, prefix="/api/vlans", tags=["vlans"])
app.include_router(devices.router, prefix="/api/devices", tags=["devices"])
app.include_router(ip_assignments.router, prefix="/api/ip-assignments", tags=["ip-assignments"])
app.include_router(audits.router, prefix="/api/audits", tags=["audits"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
