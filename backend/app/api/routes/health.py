import time
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.db.models import User
from app.db.session import AsyncSessionLocal
from app.core.config import settings
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health/detailed")
async def detailed_health_check(current_user: User = Depends(get_current_user)):
    """Detailed health check for authenticated admin users only"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    health_data = {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "database": {"status": "unknown"},
        "environment": settings.ENV,
        "version": "1.0.0"
    }
    
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            
            start_time = time.time()
            await session.execute(text("SELECT COUNT(*) FROM users"))
            query_time = time.time() - start_time
            
            health_data["database"] = {
                "status": "connected",
                "query_time_ms": round(query_time * 1000, 2)
            }
    
    except Exception as e:
        logger.error(f"Detailed health check failed: {str(e)}", exc_info=True)
        health_data["database"] = {
            "status": "error",
            "error": str(e)
        }
        health_data["status"] = "degraded"
    
    return health_data
