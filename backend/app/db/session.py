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
    """Create secure SSL context with proper certificate validation"""
    import logging
    import os
    
    logger = logging.getLogger(__name__)
    ssl_ctx = ssl.create_default_context()
    
    if settings.ENV == "development" and os.getenv("DISABLE_SSL_VERIFY") == "true":
        logger.warning("SSL verification disabled for development - NOT FOR PRODUCTION")
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
    else:
        logger.info("SSL verification enabled for secure connections")
        ssl_ctx.check_hostname = True
        ssl_ctx.verify_mode = ssl.CERT_REQUIRED
        
        ssl_ctx.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
        
        ssl_ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        
    return ssl_ctx

_ssl_ctx = _create_ssl_context()
connect_args = {"ssl": _ssl_ctx}

database_url = settings.DATABASE_URL
if database_url.startswith("sqlite"):
    engine = create_async_engine(
        database_url,
        pool_pre_ping=True,
    )
else:
    engine = create_async_engine(
        _strip_query(database_url),
        pool_pre_ping=True,
        connect_args=connect_args,
    )
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
