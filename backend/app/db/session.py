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
    import logging
    import os
    
    logger = logging.getLogger(__name__)
    fly_region = os.environ.get('FLY_REGION', 'unknown')
    fly_app_name = os.environ.get('FLY_APP_NAME', 'unknown')
    
    logger.info(f"Creating SSL context - Fly.io ENV: {fly_region}, App: {fly_app_name}")
    
    ssl_ctx = ssl.create_default_context()
    
    if settings.ENV == "production" or "sslmode=require" in settings.DATABASE_URL:
        logger.info("Production mode: Using permissive SSL for Fly.io internal connections")
        ssl_ctx.check_hostname = False  # Fly.io uses internal hostnames
        ssl_ctx.verify_mode = ssl.CERT_NONE  # Allow self-signed certs for internal connections
        
        ssl_ctx.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
        logger.info("SSL context configured for Fly.io internal database connections")
        
    else:
        logger.info("Development mode: Using minimal SSL verification")
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        
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
