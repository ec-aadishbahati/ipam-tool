from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models import Device
from app.schemas.device import DeviceCreate, DeviceOut, DeviceUpdate
from app.services.audit import record_audit

router = APIRouter()


@router.get("", response_model=list[DeviceOut])
async def list_devices(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    res = await db.execute(select(Device))
    return res.scalars().all()


@router.post("", response_model=DeviceOut)
async def create_device(payload: DeviceCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    obj = Device(name=payload.name, role=payload.role, hostname=payload.hostname, location=payload.location, vlan_id=payload.vlan_id)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    await record_audit(db, entity_type="device", entity_id=obj.id, action="create", before=None, after={"id": obj.id, "name": obj.name}, user_id=user.id)
    return obj


@router.patch("/{device_id}", response_model=DeviceOut)
async def update_device(device_id: int, payload: DeviceUpdate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    res = await db.execute(select(Device).where(Device.id == device_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    before = {"name": obj.name, "role": obj.role, "hostname": obj.hostname, "location": obj.location, "vlan_id": obj.vlan_id}
    if payload.name is not None:
        obj.name = payload.name
    if payload.role is not None:
        obj.role = payload.role
    if payload.hostname is not None:
        obj.hostname = payload.hostname
    if payload.location is not None:
        obj.location = payload.location
    if payload.vlan_id is not None:
        obj.vlan_id = payload.vlan_id
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    after = {"name": obj.name, "role": obj.role, "hostname": obj.hostname, "location": obj.location, "vlan_id": obj.vlan_id}
    await record_audit(db, entity_type="device", entity_id=obj.id, action="update", before=before, after=after, user_id=user.id)
    return obj


@router.delete("/{device_id}")
async def delete_device(device_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    await db.execute(delete(Device).where(Device.id == device_id))
    await db.commit()
    await record_audit(db, entity_type="device", entity_id=device_id, action="delete", before=None, after=None, user_id=user.id)
    return {"message": "deleted"}
