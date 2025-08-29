from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models import Subnet, Purpose, Vlan
from app.schemas.subnet import SubnetCreate, SubnetOut, SubnetUpdate
from app.services.ipam import cidr_overlap, is_gateway_valid, calculate_subnet_utilization, get_valid_ip_range
from app.services.audit import record_audit
from app.services.subnet_allocation import allocate_subnet_cidr, calculate_gateway_ip

router = APIRouter()


@router.get("", response_model=list[SubnetOut])
async def list_subnets(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    res = await db.execute(
        select(Subnet).options(
            selectinload(Subnet.supernet),
            selectinload(Subnet.purpose),
            selectinload(Subnet.vlan),
            selectinload(Subnet.ip_assignments),
        )
    )
    subnets = res.scalars().all()
    
    for subnet in subnets:
        assigned_ips = [assignment.ip_address for assignment in subnet.ip_assignments]
        subnet.utilization_percentage = calculate_subnet_utilization(subnet.cidr, assigned_ips)
        subnet.first_ip, subnet.last_ip = get_valid_ip_range(subnet.cidr)
    
    return subnets


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
    return obj


@router.delete("/{subnet_id}")
async def delete_subnet(subnet_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    await db.execute(delete(Subnet).where(Subnet.id == subnet_id))
    await db.commit()
    await record_audit(db, entity_type="subnet", entity_id=subnet_id, action="delete", before=None, after=None, user_id=user.id)
    return {"message": "deleted"}


@router.get("/export/csv")
async def export_subnets_csv(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    from fastapi.responses import StreamingResponse
    import csv
    import io
    
    res = await db.execute(select(Subnet).options(selectinload(Subnet.purpose), selectinload(Subnet.vlan)))
    subnets = res.scalars().all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["name", "cidr", "purpose", "assigned_to", "gateway_ip", "vlan", "site", "environment"])
    
    for subnet in subnets:
        writer.writerow([
            subnet.name or "",
            subnet.cidr,
            subnet.purpose.name if subnet.purpose else "",
            subnet.assigned_to or "",
            subnet.gateway_ip or "",
            f"{subnet.vlan.vlan_id} - {subnet.vlan.name}" if subnet.vlan else "",
            subnet.site or "",
            subnet.environment or ""
        ])
    
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=subnets.csv"}
    )


@router.get("/import/template")
async def get_import_template():
    from fastapi.responses import StreamingResponse
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["name", "cidr", "purpose", "assigned_to", "gateway_ip", "vlan", "site", "environment"])
    writer.writerow(["Example Subnet", "10.1.0.0/24", "Production", "Network Team", "10.1.0.1", "100 - Production", "HQ", "prod"])
    
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=subnet_import_template.csv"}
    )


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
            
            subnet = Subnet(
                name=row.get('name') or None,
                cidr=row['cidr'],
                purpose_id=purpose_id,
                assigned_to=row.get('assigned_to') or None,
                gateway_ip=row.get('gateway_ip') or None,
                vlan_id=vlan_id,
                site=row.get('site') or None,
                environment=row.get('environment') or None,
                allocation_mode="manual",
                gateway_mode="manual" if row.get('gateway_ip') else "none"
            )
            
            db.add(subnet)
            imported_count += 1
            
        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")
    
    if imported_count > 0:
        await db.commit()
    
    return {
        "imported_count": imported_count,
        "errors": errors
    }
