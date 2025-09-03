from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models import Rack, Device
from app.schemas.rack import RackCreate, RackOut, RackUpdate
from app.schemas.bulk import BulkDeleteRequest, BulkDeleteResponse, BulkExportRequest
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


@router.delete("/bulk")
async def bulk_delete_racks(payload: BulkDeleteRequest, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    deleted_count = 0
    errors = []
    
    for rack_id in payload.ids:
        try:
            in_use_device = await db.execute(select(Device).where(Device.rack_id == rack_id))
            if in_use_device.first():
                errors.append(f"Rack {rack_id} is in use by device")
                continue
                
            result = await db.execute(select(Rack).where(Rack.id == rack_id))
            rack = result.scalar_one_or_none()
            if rack:
                await db.execute(delete(Rack).where(Rack.id == rack_id))
                await record_audit(db, entity_type="rack", entity_id=rack_id, action="bulk_delete", before=None, after=None, user_id=user.id)
                deleted_count += 1
            else:
                errors.append(f"Rack with ID {rack_id} not found")
        except Exception as e:
            errors.append(f"Failed to delete rack {rack_id}: {str(e)}")
    
    if deleted_count > 0:
        await db.commit()
    
    return BulkDeleteResponse(deleted_count=deleted_count, errors=errors)


@router.delete("/{rack_id}")
async def delete_rack(rack_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    in_use_device = await db.execute(select(Device).where(Device.rack_id == rack_id))
    if in_use_device.first():
        raise HTTPException(status_code=400, detail="Rack in use by device")
    await db.execute(delete(Rack).where(Rack.id == rack_id))
    await db.commit()
    await record_audit(db, entity_type="rack", entity_id=rack_id, action="delete", before=None, after=None, user_id=user.id)
    return {"message": "deleted"}




@router.post("/export/selected")
async def export_selected_racks(payload: BulkExportRequest, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    from app.utils.csv_export import create_csv_response
    
    res = await db.execute(select(Rack).where(Rack.id.in_(payload.ids)))
    racks = res.scalars().all()
    
    data = []
    for rack in racks:
        data.append({
            "aisle": rack.aisle or "",
            "rack_number": rack.rack_number or "",
            "position_count": str(rack.position_count) if rack.position_count else "",
            "power_type": rack.power_type or "",
            "power_capacity": str(rack.power_capacity) if rack.power_capacity else "",
            "cooling_type": rack.cooling_type or "",
            "location": rack.location or "",
            "notes": rack.notes or ""
        })
    
    headers = ["aisle", "rack_number", "position_count", "power_type", "power_capacity", "cooling_type", "location", "notes"]
    return create_csv_response(data, headers, "racks-selected.csv")
