from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models import Rack, Device
from app.schemas.rack import RackCreate, RackOut, RackUpdate
from app.services.audit import record_audit

router = APIRouter()


@router.get("", response_model=list[RackOut])
async def list_racks(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    res = await db.execute(select(Rack).order_by(Rack.id.desc()))
    return res.scalars().all()


@router.post("", response_model=RackOut)
async def create_rack(payload: RackCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    exists = await db.execute(
        select(Rack).where(Rack.aisle == payload.aisle, Rack.rack_number == payload.rack_number)
    )
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Rack already exists in this aisle")
    obj = Rack(
        aisle=payload.aisle,
        rack_number=payload.rack_number,
        position_count=payload.position_count,
        power_type=payload.power_type,
        power_capacity=payload.power_capacity,
        cooling_type=payload.cooling_type,
        location=payload.location,
        notes=payload.notes,
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    await record_audit(
        db,
        entity_type="rack",
        entity_id=obj.id,
        action="create",
        before=None,
        after={"id": obj.id, "aisle": obj.aisle, "rack_number": obj.rack_number},
        user_id=user.id,
    )
    return obj


@router.patch("/{rack_id}", response_model=RackOut)
async def update_rack(rack_id: int, payload: RackUpdate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    res = await db.execute(select(Rack).where(Rack.id == rack_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    before = {"aisle": obj.aisle, "rack_number": obj.rack_number, "position_count": obj.position_count}
    if payload.aisle is not None:
        obj.aisle = payload.aisle
    if payload.rack_number is not None:
        obj.rack_number = payload.rack_number
    if payload.position_count is not None:
        obj.position_count = payload.position_count
    if payload.power_type is not None:
        obj.power_type = payload.power_type
    if payload.power_capacity is not None:
        obj.power_capacity = payload.power_capacity
    if payload.cooling_type is not None:
        obj.cooling_type = payload.cooling_type
    if payload.location is not None:
        obj.location = payload.location
    if payload.notes is not None:
        obj.notes = payload.notes
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    after = {"aisle": obj.aisle, "rack_number": obj.rack_number, "position_count": obj.position_count}
    await record_audit(db, entity_type="rack", entity_id=obj.id, action="update", before=before, after=after, user_id=user.id)
    return obj


@router.delete("/{rack_id}")
async def delete_rack(rack_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    in_use_device = await db.execute(select(Device).where(Device.rack_id == rack_id))
    if in_use_device.first():
        raise HTTPException(status_code=400, detail="Rack in use by device")
    await db.execute(delete(Rack).where(Rack.id == rack_id))
    await db.commit()
    await record_audit(db, entity_type="rack", entity_id=rack_id, action="delete", before=None, after=None, user_id=user.id)
    return {"message": "deleted"}
