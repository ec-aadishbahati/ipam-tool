from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models import AuditLog

router = APIRouter()


@router.get("")
async def list_audits(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    res = await db.execute(select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(200))
    rows = res.scalars().all()
    return [
        {
            "id": r.id,
            "entity_type": r.entity_type,
            "entity_id": r.entity_id,
            "action": r.action,
            "before": r.before,
            "after": r.after,
            "user_id": r.user_id,
            "timestamp": str(r.timestamp),
        }
        for r in rows
    ]
