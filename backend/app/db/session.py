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


def _create_ssl_context():
    """Create SSL context optimized for Fly.io PostgreSQL connections"""
    ssl_ctx = ssl.create_default_context()
    
    if settings.ENV == "production" or "sslmode=require" in settings.DATABASE_URL:
        ssl_ctx.check_hostname = False  # Fly.io uses internal hostnames
        ssl_ctx.verify_mode = ssl.CERT_REQUIRED
        
        try:
            ssl_ctx.load_verify_locations("/etc/ssl/certs/ca-certificates.crt")
        except FileNotFoundError:
            ssl_ctx.load_default_certs()
            
        ssl_ctx.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
        
    else:
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        
    return ssl_ctx

_ssl_ctx = _create_ssl_context()
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
