from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from app.core.config import settings
from urllib.parse import urlsplit, urlunsplit
import ssl


def _strip_query(url: str) -> str:
    if not url:
        return url
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", parts.fragment))


_ssl_ctx = ssl.create_default_context()
if settings.ENV == "production" or "sslmode=require" in settings.DATABASE_URL:
    _ssl_ctx.check_hostname = True
    _ssl_ctx.verify_mode = ssl.CERT_REQUIRED
    connect_args = {"ssl": _ssl_ctx}
else:
    _ssl_ctx.check_hostname = False
    _ssl_ctx.verify_mode = ssl.CERT_NONE
    connect_args = {"ssl": _ssl_ctx}

engine = create_async_engine(
    _strip_query(settings.DATABASE_URL),
    pool_pre_ping=True,
    connect_args=connect_args,
)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
