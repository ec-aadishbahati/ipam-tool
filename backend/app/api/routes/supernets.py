from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models import Supernet, Subnet, IpAssignment
from app.schemas.supernet import SupernetCreate, SupernetOut, SupernetUpdate
from app.schemas.bulk import BulkDeleteRequest, BulkDeleteResponse, BulkExportRequest
from app.services.ipam import cidr_overlap, calculate_supernet_utilization, calculate_subnet_utilization, calculate_supernet_available_ips, calculate_spatial_allocation_segments
import ipaddress
from app.services.audit import record_audit

router = APIRouter()


@router.get("", response_model=list[SupernetOut])
async def list_supernets(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    res = await db.execute(select(Supernet).options(selectinload(Supernet.subnets)).order_by(Supernet.id.desc()))
    supernets = res.scalars().all()
    
    for supernet in supernets:
        supernet.utilization_percentage = await calculate_supernet_utilization(supernet.subnets, db)
        supernet.available_ips = calculate_supernet_available_ips(supernet.cidr, supernet.subnets)
        supernet.spatial_segments = calculate_spatial_allocation_segments(supernet.cidr, supernet.subnets)
    
    return supernets


@router.post("", response_model=SupernetOut)
async def create_supernet(payload: SupernetCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    res = await db.execute(select(Supernet).where(Supernet.cidr == payload.cidr))
    if res.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Supernet already exists")
    obj = Supernet(cidr=payload.cidr, name=payload.name, site=payload.site, environment=payload.environment)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    await record_audit(db, entity_type="supernet", entity_id=obj.id, action="create", before=None, after={"id": obj.id, "cidr": obj.cidr}, user_id=user.id)
    return obj


@router.patch("/{supernet_id}", response_model=SupernetOut)
async def update_supernet(supernet_id: int, payload: SupernetUpdate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    res = await db.execute(select(Supernet).where(Supernet.id == supernet_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    before = {"cidr": obj.cidr, "name": obj.name, "site": obj.site, "environment": obj.environment}
    if payload.cidr is not None:
        obj.cidr = payload.cidr
    if payload.name is not None:
        obj.name = payload.name
    if payload.site is not None:
        obj.site = payload.site
    if payload.environment is not None:
        obj.environment = payload.environment
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    after = {"cidr": obj.cidr, "name": obj.name, "site": obj.site, "environment": obj.environment}
    await record_audit(db, entity_type="supernet", entity_id=obj.id, action="update", before=before, after=after, user_id=user.id)
    return obj


@router.delete("/{supernet_id}")
async def delete_supernet(supernet_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    res = await db.execute(select(Subnet).where(Subnet.supernet_id == supernet_id))
    if res.first():
        raise HTTPException(status_code=400, detail="Cannot delete supernet with subnets")
    await db.execute(delete(Supernet).where(Supernet.id == supernet_id))
    await db.commit()
    await record_audit(db, entity_type="supernet", entity_id=supernet_id, action="delete", before=None, after=None, user_id=user.id)
    return {"message": "deleted"}


@router.delete("/bulk")
async def bulk_delete_supernets(payload: BulkDeleteRequest, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    deleted_count = 0
    errors = []
    
    for supernet_id in payload.ids:
        try:
            res = await db.execute(select(Subnet).where(Subnet.supernet_id == supernet_id))
            if res.first():
                errors.append(f"Cannot delete supernet {supernet_id} with subnets")
                continue
                
            result = await db.execute(select(Supernet).where(Supernet.id == supernet_id))
            supernet = result.scalar_one_or_none()
            if supernet:
                await db.execute(delete(Supernet).where(Supernet.id == supernet_id))
                await record_audit(db, entity_type="supernet", entity_id=supernet_id, action="bulk_delete", before=None, after=None, user_id=user.id)
                deleted_count += 1
            else:
                errors.append(f"Supernet with ID {supernet_id} not found")
        except Exception as e:
            errors.append(f"Failed to delete supernet {supernet_id}: {str(e)}")
    
    if deleted_count > 0:
        await db.commit()
    
    return BulkDeleteResponse(deleted_count=deleted_count, errors=errors)


@router.post("/export/selected")
async def export_selected_supernets(payload: BulkExportRequest, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    from app.utils.csv_export import create_csv_response
    
    res = await db.execute(
        select(Supernet).options(selectinload(Supernet.subnets))
        .where(Supernet.id.in_(payload.ids))
    )
    supernets = res.scalars().all()
    
    data = []
    for supernet in supernets:
        assigned_cidrs = [s.cidr for s in supernet.subnets]
        utilization = calculate_supernet_utilization(supernet.cidr, assigned_cidrs)
        
        data.append({
            "name": supernet.name or "",
            "cidr": supernet.cidr or "",
            "site": supernet.site or "",
            "environment": supernet.environment or "",
            "utilization": f"{utilization:.1f}%"
        })
    
    headers = ["name", "cidr", "site", "environment", "utilization"]
    return create_csv_response(data, headers, "supernets-selected.csv")


@router.get("/export/csv")
async def export_supernets_csv(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    from app.utils.csv_export import create_csv_response
    
    res = await db.execute(select(Supernet))
    supernets = res.scalars().all()
    
    data = []
    for supernet in supernets:
        data.append({
            "name": supernet.name or "",
            "cidr": supernet.cidr,
            "site": supernet.site or "",
            "environment": supernet.environment or ""
        })
    
    headers = ["name", "cidr", "site", "environment"]
    return create_csv_response(data, headers, "supernets.csv")
