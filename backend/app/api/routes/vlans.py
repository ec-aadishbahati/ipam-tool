from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models import Vlan, Subnet, Device
from app.schemas.vlan import VlanCreate, VlanOut, VlanUpdate
from app.schemas.pagination import PaginatedResponse
from app.schemas.bulk import BulkDeleteRequest, BulkDeleteResponse, BulkExportRequest
from app.services.audit import record_audit

router = APIRouter()


@router.get("", response_model=PaginatedResponse[VlanOut])
async def list_vlans(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(75, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db), 
    user=Depends(get_current_user)
):
    count_result = await db.execute(select(func.count(Vlan.id)))
    total = count_result.scalar()
    
    offset = (page - 1) * limit
    res = await db.execute(select(Vlan).order_by(Vlan.id.desc()).offset(offset).limit(limit))
    vlans = res.scalars().all()
    
    return PaginatedResponse.create(vlans, total, page, limit)


@router.post("", response_model=VlanOut)
async def create_vlan(payload: VlanCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    exists = await db.execute(
        select(Vlan).where(Vlan.site == payload.site, Vlan.environment == payload.environment, Vlan.vlan_id == payload.vlan_id)
    )
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="VLAN already exists in site/environment")
    obj = Vlan(
        site=payload.site,
        environment=payload.environment,
        vlan_id=payload.vlan_id,
        name=payload.name,
        purpose_id=payload.purpose_id,
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    await record_audit(
        db,
        entity_type="vlan",
        entity_id=obj.id,
        action="create",
        before=None,
        after={"id": obj.id, "site": obj.site, "environment": obj.environment, "vlan_id": obj.vlan_id},
        user_id=user.id,
    )
    return obj


@router.patch("/{vlan_id}", response_model=VlanOut)
async def update_vlan(vlan_id: int, payload: VlanUpdate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    res = await db.execute(select(Vlan).where(Vlan.id == vlan_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    before = {"site": obj.site, "environment": obj.environment, "vlan_id": obj.vlan_id, "name": obj.name, "purpose_id": obj.purpose_id}
    if payload.site is not None:
        obj.site = payload.site
    if payload.environment is not None:
        obj.environment = payload.environment
    if payload.vlan_id is not None:
        obj.vlan_id = payload.vlan_id
    if payload.name is not None:
        obj.name = payload.name
    if payload.purpose_id is not None:
        obj.purpose_id = payload.purpose_id
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    after = {"site": obj.site, "environment": obj.environment, "vlan_id": obj.vlan_id, "name": obj.name, "purpose_id": obj.purpose_id}
    await record_audit(db, entity_type="vlan", entity_id=obj.id, action="update", before=before, after=after, user_id=user.id)
    return obj


@router.delete("/bulk")
async def bulk_delete_vlans(payload: BulkDeleteRequest, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    deleted_count = 0
    errors = []
    
    for vlan_id in payload.ids:
        try:
            in_use_subnet = await db.execute(select(Subnet).where(Subnet.vlan_id == vlan_id))
            if in_use_subnet.first():
                errors.append(f"VLAN {vlan_id} is in use by subnet")
                continue
            in_use_device = await db.execute(select(Device).where(Device.vlan_id == vlan_id))
            if in_use_device.first():
                errors.append(f"VLAN {vlan_id} is in use by device")
                continue
                
            result = await db.execute(select(Vlan).where(Vlan.id == vlan_id))
            vlan = result.scalar_one_or_none()
            if vlan:
                await db.execute(delete(Vlan).where(Vlan.id == vlan_id))
                await record_audit(db, entity_type="vlan", entity_id=vlan_id, action="bulk_delete", before=None, after=None, user_id=user.id)
                deleted_count += 1
            else:
                errors.append(f"VLAN with ID {vlan_id} not found")
        except Exception as e:
            errors.append(f"Failed to delete VLAN {vlan_id}: {str(e)}")
    
    if deleted_count > 0:
        await db.commit()
    
    return BulkDeleteResponse(deleted_count=deleted_count, errors=errors)


@router.delete("/{vlan_id}")
async def delete_vlan(vlan_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    in_use_subnet = await db.execute(select(Subnet).where(Subnet.vlan_id == vlan_id))
    if in_use_subnet.first():
        raise HTTPException(status_code=400, detail="VLAN in use by subnet")
    in_use_device = await db.execute(select(Device).where(Device.vlan_id == vlan_id))
    if in_use_device.first():
        raise HTTPException(status_code=400, detail="VLAN in use by device")
    await db.execute(delete(Vlan).where(Vlan.id == vlan_id))
    await db.commit()
    await record_audit(db, entity_type="vlan", entity_id=vlan_id, action="delete", before=None, after=None, user_id=user.id)
    return {"message": "deleted"}




@router.post("/export/selected")
async def export_selected_vlans(payload: BulkExportRequest, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    from app.utils.csv_export import create_csv_response
    
    res = await db.execute(select(Vlan).where(Vlan.id.in_(payload.ids)))
    vlans = res.scalars().all()
    
    data = []
    for vlan in vlans:
        data.append({
            "site": vlan.site or "",
            "environment": vlan.environment or "",
            "vlan_id": str(vlan.vlan_id),
            "name": vlan.name or "",
            "purpose_id": str(vlan.purpose_id) if vlan.purpose_id else ""
        })
    
    headers = ["site", "environment", "vlan_id", "name", "purpose_id"]
    return create_csv_response(data, headers, "vlans-selected.csv")
