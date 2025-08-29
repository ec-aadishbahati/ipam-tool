from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models import Supernet, Subnet
from app.schemas.supernet import SupernetCreate, SupernetOut, SupernetUpdate
from app.services.ipam import cidr_overlap, calculate_subnet_utilization, calculate_subnet_utilization
from app.db.models import IpAssignment
import ipaddress
from app.services.audit import record_audit

router = APIRouter()


@router.get("", response_model=list[SupernetOut])
async def list_supernets(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    res = await db.execute(select(Supernet).options(selectinload(Supernet.subnets)))
    supernets = res.scalars().all()
    
    for supernet in supernets:
        total_assigned = 0
        total_usable = 0
        
        for subnet in supernet.subnets:
            subnet_res = await db.execute(select(IpAssignment).where(IpAssignment.subnet_id == subnet.id))
            assigned_ips = [assignment.ip_address for assignment in subnet_res.scalars().all()]
            
            network = ipaddress.ip_network(subnet.cidr, strict=False)
            total_assigned += len(assigned_ips)
            if network.prefixlen == network.max_prefixlen:
                total_usable += 1
            elif network.prefixlen == 31:
                total_usable += 2
            else:
                total_usable += len(list(network.hosts()))
        
        supernet.utilization_percentage = (total_assigned / total_usable * 100) if total_usable > 0 else 0.0
    
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
