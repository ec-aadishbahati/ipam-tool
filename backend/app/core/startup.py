import logging
import os
from app.core.config import settings

logger = logging.getLogger(__name__)

def validate_environment():
    """Validate that all required environment variables are set"""
    required_vars = [
        "DATABASE_URL",
        "JWT_SECRET_KEY", 
        "JWT_REFRESH_SECRET_KEY",
        "ADMIN_USERNAME",
        "ADMIN_PASSWORD", 
        "ADMIN_EMAIL"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not getattr(settings, var, None):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        raise ValueError(f"Missing required environment variables: {missing_vars}")
    
    if settings.ENV == "production":
        if "sslmode=disable" in settings.DATABASE_URL:
            raise ValueError("SSL must be enabled for production database connections")
        
        if not settings.DATABASE_URL.startswith("postgresql+asyncpg://"):
            logger.warning("Consider using PostgreSQL with asyncpg for production")
        
        if "sslmode=" not in settings.DATABASE_URL:
            logger.warning("Adding sslmode=require to database URL")
            settings.DATABASE_URL += "?sslmode=require"
    
    if settings.CORS_ORIGIN_REGEX:
        logger.info(f"CORS regex configured: {settings.CORS_ORIGIN_REGEX}")
    if settings.CORS_ORIGINS:
        logger.info(f"CORS origins configured: {settings.CORS_ORIGINS}")
    
    fly_region = os.environ.get('FLY_REGION', 'unknown')
    fly_app_name = os.environ.get('FLY_APP_NAME', 'unknown')
    fly_alloc_id = os.environ.get('FLY_ALLOC_ID', 'unknown')
    logger.info(f"Running in Fly.io ENV - Region: {fly_region}, App: {fly_app_name}, Alloc: {fly_alloc_id}")
    
    logger.info("SSL configuration validated")
    logger.info("Environment validation passed")
