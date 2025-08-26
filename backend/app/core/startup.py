import logging
import os
from app.core.config import settings

logger = logging.getLogger(__name__)

def validate_environment():
    """Validate that all required environment variables are set"""
    required_vars = [
        "DATABASE_URL",
        "JWT_SECRET_KEY", 
        "JWT_REFRESH_SECRET_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not getattr(settings, var, None):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        raise ValueError(f"Missing required environment variables: {missing_vars}")
    
    if settings.CORS_ORIGIN_REGEX:
        logger.info(f"CORS regex configured: {settings.CORS_ORIGIN_REGEX}")
    if settings.CORS_ORIGINS:
        logger.info(f"CORS origins configured: {settings.CORS_ORIGINS}")
    
    fly_region = os.environ.get('FLY_REGION', 'unknown')
    logger.info(f"Running in Fly.io ENV: {fly_region}")
    
    logger.info("Environment validation passed")
