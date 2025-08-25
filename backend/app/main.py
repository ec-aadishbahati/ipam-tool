from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.db.session import engine
from app.api.routes import auth, purposes, supernets, subnets, vlans
from app.api.routes import devices, ip_assignments, audits, search


def _parse_origins(origins_str: str) -> list[str]:
    if not origins_str:
        return []
    return [o.strip() for o in origins_str.replace(" ", "").split(",") if o.strip()]


app = FastAPI(title="IPAM")

cors_kwargs = {
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}
origin_list = _parse_origins(settings.CORS_ORIGINS)
if origin_list:
    cors_kwargs["allow_origins"] = origin_list
if settings.CORS_ORIGIN_REGEX:
    cors_kwargs["allow_origin_regex"] = settings.CORS_ORIGIN_REGEX

app.add_middleware(CORSMiddleware, **cors_kwargs)


@app.get("/healthz")
async def healthz():
    async with AsyncSession(engine) as session:
        await session.execute(text("SELECT 1"))
    return {"status": "ok"}


app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(purposes.router, prefix="/purposes", tags=["purposes"])
app.include_router(supernets.router, prefix="/supernets", tags=["supernets"])
app.include_router(subnets.router, prefix="/subnets", tags=["subnets"])
app.include_router(vlans.router, prefix="/vlans", tags=["vlans"])
app.include_router(devices.router, prefix="/devices", tags=["devices"])
app.include_router(ip_assignments.router, prefix="/ip-assignments", tags=["ip-assignments"])
app.include_router(audits.router, prefix="/audits", tags=["audits"])
app.include_router(search.router, prefix="/search", tags=["search"])
