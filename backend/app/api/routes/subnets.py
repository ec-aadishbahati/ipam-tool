from fastapi import APIRouter, Depends, HTTPException, UploadFile, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from sqlalchemy.orm import selectinload
from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models import Subnet, Purpose, Vlan, Supernet
from app.schemas.subnet import SubnetCreate, SubnetOut, SubnetUpdate
from app.schemas.pagination import PaginatedResponse
from app.services.ipam import cidr_overlap, is_gateway_valid, calculate_subnet_utilization, get_valid_ip_range, calculate_supernet_utilization, cidr_contains, calculate_subnet_available_ips, calculate_subnet_spatial_segments
from app.services.audit import record_audit
from app.services.subnet_allocation import allocate_subnet_cidr, calculate_gateway_ip

router = APIRouter()


@router.get("", response_model=PaginatedResponse[SubnetOut])
async def list_subnets(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(75, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db), 
    user=Depends(get_current_user)
):
    count_result = await db.execute(select(func.count(Subnet.id)))
    total = count_result.scalar()
    
    offset = (page - 1) * limit
    res = await db.execute(
        select(Subnet).options(
            selectinload(Subnet.supernet),
            selectinload(Subnet.purpose),
            selectinload(Subnet.vlan),
            selectinload(Subnet.ip_assignments),
        ).order_by(Subnet.id.desc()).offset(offset).limit(limit)
    )
    subnets = res.scalars().all()
    
    for subnet in subnets:
        assigned_ips = [assignment.ip_address for assignment in subnet.ip_assignments]
        subnet.utilization_percentage = calculate_subnet_utilization(subnet.cidr, assigned_ips)
        subnet.available_ips = calculate_subnet_available_ips(subnet.cidr, assigned_ips)
        subnet.first_ip, subnet.last_ip = get_valid_ip_range(subnet.cidr)
        subnet.spatial_segments = calculate_subnet_spatial_segments(subnet.cidr, assigned_ips)
    
    return PaginatedResponse.create(subnets, total, page, limit)


@router.post("", response_model=SubnetOut)
async def create_subnet(payload: SubnetCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    try:
        allocated_cidr = await allocate_subnet_cidr(
            db=db,
            allocation_mode=payload.allocation_mode,
            supernet_id=payload.supernet_id,
            manual_cidr=payload.cidr,
            subnet_mask=payload.subnet_mask,
            host_count=payload.host_count
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    existing = await db.execute(select(Subnet))
    for s in existing.scalars().all():
        if cidr_overlap(s.cidr, allocated_cidr):
            raise HTTPException(status_code=400, detail="Overlapping subnet")
    
    gateway_ip = payload.gateway_ip
    if payload.gateway_mode == "auto_first":
        gateway_ip = calculate_gateway_ip(allocated_cidr, payload.gateway_mode)
    elif payload.gateway_mode == "none":
        gateway_ip = None
    
    if gateway_ip and not is_gateway_valid(gateway_ip, allocated_cidr):
        raise HTTPException(status_code=400, detail="Invalid gateway for subnet")
    
    obj = Subnet(
        cidr=allocated_cidr,
        name=payload.name,
        purpose_id=payload.purpose_id,
        assigned_to=payload.assigned_to,
        gateway_ip=gateway_ip,
        vlan_id=payload.vlan_id,
        site=payload.site,
        environment=payload.environment,
        supernet_id=payload.supernet_id,
        allocation_mode=payload.allocation_mode,
        gateway_mode=payload.gateway_mode,
        subnet_mask=payload.subnet_mask,
        host_count=payload.host_count,
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    await record_audit(db, entity_type="subnet", entity_id=obj.id, action="create", before=None, after={"id": obj.id, "cidr": obj.cidr}, user_id=user.id)
    
    if obj.supernet_id:
        supernet_res = await db.execute(select(Supernet).options(selectinload(Supernet.subnets)).where(Supernet.id == obj.supernet_id))
        supernet = supernet_res.scalar_one_or_none()
        if supernet:
            supernet.utilization_percentage = await calculate_supernet_utilization(supernet.subnets, db)
            db.add(supernet)
            await db.commit()
    
    return obj


@router.patch("/{subnet_id}", response_model=SubnetOut)
async def update_subnet(subnet_id: int, payload: SubnetUpdate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    res = await db.execute(select(Subnet).where(Subnet.id == subnet_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    before = {
        "cidr": obj.cidr,
        "name": obj.name,
        "purpose_id": obj.purpose_id,
        "assigned_to": obj.assigned_to,
        "gateway_ip": obj.gateway_ip,
        "vlan_id": obj.vlan_id,
        "site": obj.site,
        "environment": obj.environment,
        "supernet_id": obj.supernet_id,
    }
    if payload.cidr is not None:
        existing = await db.execute(select(Subnet).where(Subnet.id != subnet_id))
        for s in existing.scalars().all():
            if cidr_overlap(s.cidr, payload.cidr):
                raise HTTPException(status_code=400, detail="Overlapping subnet")
        obj.cidr = payload.cidr
    if payload.name is not None:
        obj.name = payload.name
    if payload.purpose_id is not None:
        obj.purpose_id = payload.purpose_id
    if payload.assigned_to is not None:
        obj.assigned_to = payload.assigned_to
    if payload.gateway_ip is not None:
        if payload.gateway_ip and not is_gateway_valid(payload.gateway_ip, obj.cidr):
            raise HTTPException(status_code=400, detail="Invalid gateway for subnet")
        obj.gateway_ip = payload.gateway_ip
    if payload.vlan_id is not None:
        obj.vlan_id = payload.vlan_id
    if payload.site is not None:
        obj.site = payload.site
    if payload.environment is not None:
        obj.environment = payload.environment
    if payload.supernet_id is not None:
        obj.supernet_id = payload.supernet_id
    if payload.allocation_mode is not None:
        obj.allocation_mode = payload.allocation_mode
    if payload.gateway_mode is not None:
        obj.gateway_mode = payload.gateway_mode
    if payload.subnet_mask is not None:
        obj.subnet_mask = payload.subnet_mask
    if payload.host_count is not None:
        obj.host_count = payload.host_count
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    after = {
        "cidr": obj.cidr,
        "name": obj.name,
        "purpose_id": obj.purpose_id,
        "assigned_to": obj.assigned_to,
        "gateway_ip": obj.gateway_ip,
        "vlan_id": obj.vlan_id,
        "site": obj.site,
        "environment": obj.environment,
        "supernet_id": obj.supernet_id,
    }
    await record_audit(db, entity_type="subnet", entity_id=obj.id, action="update", before=before, after=after, user_id=user.id)
    
    supernet_ids = set()
    if before.get("supernet_id"):
        supernet_ids.add(before["supernet_id"])
    if obj.supernet_id:
        supernet_ids.add(obj.supernet_id)
    
    for supernet_id in supernet_ids:
        supernet_res = await db.execute(select(Supernet).options(selectinload(Supernet.subnets)).where(Supernet.id == supernet_id))
        supernet = supernet_res.scalar_one_or_none()
        if supernet:
            supernet.utilization_percentage = await calculate_supernet_utilization(supernet.subnets, db)
            db.add(supernet)
    
    if supernet_ids:
        await db.commit()
    
    return obj


@router.delete("/{subnet_id}")
async def delete_subnet(subnet_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    subnet_res = await db.execute(select(Subnet).where(Subnet.id == subnet_id))
    subnet = subnet_res.scalar_one_or_none()
    supernet_id = subnet.supernet_id if subnet else None
    
    await db.execute(delete(Subnet).where(Subnet.id == subnet_id))
    await db.commit()
    await record_audit(db, entity_type="subnet", entity_id=subnet_id, action="delete", before=None, after=None, user_id=user.id)
    
    if supernet_id:
        supernet_res = await db.execute(select(Supernet).options(selectinload(Supernet.subnets)).where(Supernet.id == supernet_id))
        supernet = supernet_res.scalar_one_or_none()
        if supernet:
            supernet.utilization_percentage = await calculate_supernet_utilization(supernet.subnets, db)
            db.add(supernet)
            await db.commit()
    
    return {"message": "deleted"}


@router.get("/export/csv")
async def export_subnets_csv(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    from app.utils.csv_export import create_csv_response
    
    res = await db.execute(select(Subnet).options(selectinload(Subnet.purpose), selectinload(Subnet.vlan)))
    subnets = res.scalars().all()
    
    data = []
    for subnet in subnets:
        data.append({
            "name": subnet.name or "",
            "cidr": subnet.cidr,
            "purpose": subnet.purpose.name if subnet.purpose else "",
            "assigned_to": subnet.assigned_to or "",
            "gateway_ip": subnet.gateway_ip or "",
            "vlan": f"{subnet.vlan.vlan_id} - {subnet.vlan.name}" if subnet.vlan else "",
            "site": subnet.site or "",
            "environment": subnet.environment or ""
        })
    
    headers = ["name", "cidr", "purpose", "assigned_to", "gateway_ip", "vlan", "site", "environment"]
    return create_csv_response(data, headers, "subnets.csv")


@router.get("/import/template")
async def get_import_template():
    from app.utils.csv_export import create_csv_template
    
    headers = ["name", "cidr", "purpose", "assigned_to", "gateway_ip", "vlan", "site", "environment"]
    sample_data = ["Example Subnet", "10.1.0.0/24", "Production", "Network Team", "10.1.0.1", "100 - Production", "HQ", "prod"]
    return create_csv_template(headers, sample_data, "subnet_import_template.csv")


@router.post("/import/csv")
async def import_subnets_csv(file: UploadFile, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    import csv
    import io
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    content = await file.read()
    csv_data = io.StringIO(content.decode('utf-8'))
    reader = csv.DictReader(csv_data)
    
    imported_count = 0
    errors = []
    
    for row_num, row in enumerate(reader, start=2):
        try:
            existing = await db.execute(select(Subnet).where(Subnet.cidr == row['cidr']))
            if existing.scalar_one_or_none():
                errors.append(f"Row {row_num}: Subnet with CIDR {row['cidr']} already exists")
                continue
            
            purpose_id = None
            if row.get('purpose'):
                purpose_res = await db.execute(select(Purpose).where(Purpose.name == row['purpose']))
                purpose = purpose_res.scalar_one_or_none()
                if purpose:
                    purpose_id = purpose.id
            
            vlan_id = None
            if row.get('vlan') and ' - ' in row['vlan']:
                vlan_id_str = row['vlan'].split(' - ')[0]
                try:
                    vlan_res = await db.execute(select(Vlan).where(Vlan.vlan_id == int(vlan_id_str)))
                    vlan = vlan_res.scalar_one_or_none()
                    if vlan:
                        vlan_id = vlan.id
                except ValueError:
                    pass
            
            supernet_id = None
            if row['cidr']:
                supernets_res = await db.execute(select(Supernet))
                supernets = supernets_res.scalars().all()
                
                for supernet in supernets:
                    if cidr_contains(supernet.cidr, row['cidr']):
                        supernet_id = supernet.id
                        break
            
            subnet = Subnet(
                name=row.get('name') or None,
                cidr=row['cidr'],
                purpose_id=purpose_id,
                assigned_to=row.get('assigned_to') or None,
                gateway_ip=row.get('gateway_ip') or None,
                vlan_id=vlan_id,
                site=row.get('site') or None,
                environment=row.get('environment') or None,
                supernet_id=supernet_id,
                allocation_mode="manual",
                gateway_mode="manual" if row.get('gateway_ip') else "none"
            )
            
            db.add(subnet)
            imported_count += 1
            
        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")
    
    if imported_count > 0:
        await db.commit()
        
        supernet_res = await db.execute(select(Supernet).options(selectinload(Supernet.subnets)))
        supernets = supernet_res.scalars().all()
        for supernet in supernets:
            supernet.utilization_percentage = await calculate_supernet_utilization(supernet.subnets, db)
            db.add(supernet)
        
        if supernets:
            await db.commit()
    
    return {
        "imported_count": imported_count,
        "errors": errors
    }
