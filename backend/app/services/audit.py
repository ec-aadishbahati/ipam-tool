import json
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import AuditLog


async def record_audit(db: AsyncSession, *, entity_type: str, entity_id: int, action: str, before: dict | None, after: dict | None, user_id: int | None):
    log = AuditLog(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        before=json.dumps(before) if before is not None else None,
        after=json.dumps(after) if after is not None else None,
        user_id=user_id,
    )
    db.add(log)
    await db.commit()
