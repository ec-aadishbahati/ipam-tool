from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models import Category
from app.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate
from app.services.audit import record_audit

router = APIRouter()


@router.get("", response_model=list[CategoryOut])
async def list_categories(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    res = await db.execute(select(Category).order_by(Category.name))
    return res.scalars().all()


@router.post("", response_model=CategoryOut)
async def create_category(payload: CategoryCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    q = await db.execute(select(Category).where(Category.name == payload.name))
    if q.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Category already exists")
    obj = Category(name=payload.name, description=payload.description)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    await record_audit(db, entity_type="category", entity_id=obj.id, action="create", before=None, after={"id": obj.id, "name": obj.name}, user_id=user.id)
    return obj


@router.patch("/{category_id}", response_model=CategoryOut)
async def update_category(category_id: int, payload: CategoryUpdate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    res = await db.execute(select(Category).where(Category.id == category_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    before = {"id": obj.id, "name": obj.name, "description": obj.description}
    if payload.name is not None:
        obj.name = payload.name
    if payload.description is not None:
        obj.description = payload.description
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    after = {"id": obj.id, "name": obj.name, "description": obj.description}
    await record_audit(db, entity_type="category", entity_id=obj.id, action="update", before=before, after=after, user_id=user.id)
    return obj


@router.delete("/{category_id}")
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    await db.execute(delete(Category).where(Category.id == category_id))
    await db.commit()
    await record_audit(db, entity_type="category", entity_id=category_id, action="delete", before=None, after=None, user_id=user.id)
    return {"message": "deleted"}
