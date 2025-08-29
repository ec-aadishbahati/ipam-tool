from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models import Purpose
from app.schemas.purpose import PurposeCreate, PurposeOut, PurposeUpdate
from app.services.audit import record_audit

router = APIRouter()


@router.get("", response_model=list[PurposeOut])
async def list_purposes(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    res = await db.execute(select(Purpose).options(selectinload(Purpose.category)).order_by(Purpose.name))
    return res.scalars().all()


@router.post("", response_model=PurposeOut)
async def create_purpose(payload: PurposeCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    q = await db.execute(select(Purpose).where(Purpose.name == payload.name))
    if q.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Purpose already exists")
    obj = Purpose(name=payload.name, description=payload.description, category_id=payload.category_id)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    await record_audit(db, entity_type="purpose", entity_id=obj.id, action="create", before=None, after={"id": obj.id, "name": obj.name}, user_id=user.id)
    return obj


@router.patch("/{purpose_id}", response_model=PurposeOut)
async def update_purpose(purpose_id: int, payload: PurposeUpdate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    res = await db.execute(select(Purpose).options(selectinload(Purpose.category)).where(Purpose.id == purpose_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    before = {"id": obj.id, "name": obj.name, "description": obj.description, "category_id": obj.category_id}
    if payload.name is not None:
        obj.name = payload.name
    if payload.description is not None:
        obj.description = payload.description
    if payload.category_id is not None:
        obj.category_id = payload.category_id
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    after = {"id": obj.id, "name": obj.name, "description": obj.description, "category_id": obj.category_id}
    await record_audit(db, entity_type="purpose", entity_id=obj.id, action="update", before=before, after=after, user_id=user.id)
    return obj


@router.delete("/{purpose_id}")
async def delete_purpose(purpose_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    await db.execute(delete(Purpose).where(Purpose.id == purpose_id))
    await db.commit()
    await record_audit(db, entity_type="purpose", entity_id=purpose_id, action="delete", before=None, after=None, user_id=user.id)
    return {"message": "deleted"}
