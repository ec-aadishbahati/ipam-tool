from fastapi import APIRouter, Depends, HTTPException, UploadFile, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from sqlalchemy.orm import selectinload
from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models import IpAssignment, Subnet
from app.schemas.ip_assignment import IpAssignmentCreate, IpAssignmentOut, IpAssignmentUpdate
from app.schemas.pagination import PaginatedResponse
from app.services.ipam import ip_in_cidr, is_usable_ip_in_subnet
from app.services.audit import record_audit

router = APIRouter()


@router.get("", response_model=PaginatedResponse[IpAssignmentOut])
async def list_ip_assignments(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(75, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db), 
    user=Depends(get_current_user)
):
    count_result = await db.execute(select(func.count(IpAssignment.id)))
    total = count_result.scalar()
    
    offset = (page - 1) * limit
    res = await db.execute(
        select(IpAssignment).options(
            selectinload(IpAssignment.subnet), selectinload(IpAssignment.device)
        ).offset(offset).limit(limit)
    )
    ip_assignments = res.scalars().all()
    
    return PaginatedResponse.create(ip_assignments, total, page, limit)


@router.post("", response_model=IpAssignmentOut)
async def create_ip_assignment(payload: IpAssignmentCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    subnet_res = await db.execute(select(Subnet).where(Subnet.id == payload.subnet_id))
    subnet = subnet_res.scalar_one_or_none()
    if not subnet:
        raise HTTPException(status_code=400, detail="Subnet not found")
    if not ip_in_cidr(payload.ip_address, subnet.cidr) or not is_usable_ip_in_subnet(payload.ip_address, subnet.cidr):
        raise HTTPException(status_code=400, detail="IP not in subnet or not usable")
    if subnet.gateway_ip and payload.ip_address == subnet.gateway_ip:
        raise HTTPException(status_code=400, detail="IP cannot be gateway")
    existing = await db.execute(
        select(IpAssignment).where(IpAssignment.subnet_id == payload.subnet_id, IpAssignment.ip_address == payload.ip_address)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="IP already assigned in subnet")
    obj = IpAssignment(subnet_id=payload.subnet_id, device_id=payload.device_id, ip_address=payload.ip_address, role=payload.role, interface=payload.interface)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    await record_audit(
        db, entity_type="ip_assignment", entity_id=obj.id, action="create", before=None, after={"id": obj.id, "ip": obj.ip_address}, user_id=user.id
    )
    return obj


@router.patch("/{assignment_id}", response_model=IpAssignmentOut)
async def update_ip_assignment(assignment_id: int, payload: IpAssignmentUpdate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    res = await db.execute(select(IpAssignment).where(IpAssignment.id == assignment_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    before = {"device_id": obj.device_id, "ip_address": obj.ip_address, "role": obj.role, "interface": obj.interface}
    if payload.ip_address is not None:
        subnet_res = await db.execute(select(Subnet).where(Subnet.id == obj.subnet_id))
        subnet = subnet_res.scalar_one_or_none()
        if not subnet:
            raise HTTPException(status_code=400, detail="Subnet not found")
        if not ip_in_cidr(payload.ip_address, subnet.cidr) or not is_usable_ip_in_subnet(payload.ip_address, subnet.cidr):
            raise HTTPException(status_code=400, detail="IP not in subnet or not usable")
        if subnet.gateway_ip and payload.ip_address == subnet.gateway_ip:
            raise HTTPException(status_code=400, detail="IP cannot be gateway")
        dup = await db.execute(
            select(IpAssignment).where(
                IpAssignment.subnet_id == obj.subnet_id, IpAssignment.ip_address == payload.ip_address, IpAssignment.id != assignment_id
            )
        )
        if dup.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="IP already assigned in subnet")
        obj.ip_address = payload.ip_address
    if payload.device_id is not None:
        obj.device_id = payload.device_id
    if payload.role is not None:
        obj.role = payload.role
    if payload.interface is not None:
        obj.interface = payload.interface
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    after = {"device_id": obj.device_id, "ip_address": obj.ip_address, "role": obj.role, "interface": obj.interface}
    await record_audit(db, entity_type="ip_assignment", entity_id=obj.id, action="update", before=before, after=after, user_id=user.id)
    return obj


@router.delete("/{assignment_id}")
async def delete_ip_assignment(assignment_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    await db.execute(delete(IpAssignment).where(IpAssignment.id == assignment_id))
    await db.commit()
    await record_audit(db, entity_type="ip_assignment", entity_id=assignment_id, action="delete", before=None, after=None, user_id=user.id)
    return {"message": "deleted"}


@router.get("/export/csv")
async def export_ip_assignments_csv(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    from app.utils.csv_export import create_csv_response
    
    res = await db.execute(
        select(IpAssignment).options(
            selectinload(IpAssignment.subnet),
            selectinload(IpAssignment.device)
        )
    )
    ip_assignments = res.scalars().all()
    
    data = []
    for ip in ip_assignments:
        data.append({
            "subnet": f"{ip.subnet.name} ({ip.subnet.cidr})" if ip.subnet else "",
            "device": ip.device.name if ip.device else "",
            "ip_address": ip.ip_address,
            "interface": ip.interface or "",
            "role": ip.role or ""
        })
    
    headers = ["subnet", "device", "ip_address", "interface", "role"]
    return create_csv_response(data, headers, "ip_assignments.csv")


@router.get("/import/template")
async def get_ip_assignment_import_template():
    from app.utils.csv_export import create_csv_template
    
    headers = ["subnet", "device", "ip_address", "interface", "role"]
    sample_data = ["Example Subnet (10.1.0.0/24)", "Server-01", "10.1.0.10", "eth0", "Management IP"]
    return create_csv_template(headers, sample_data, "ip_assignment_import_template.csv")


@router.post("/import/csv")
async def import_ip_assignments_csv(file: UploadFile, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    import csv
    import io
    from app.db.models import Subnet, Device
    from app.services.ipam import ip_in_cidr, is_usable_ip_in_subnet
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    content = await file.read()
    csv_data = io.StringIO(content.decode('utf-8'))
    reader = csv.DictReader(csv_data)
    
    imported_count = 0
    errors = []
    
    for row_num, row in enumerate(reader, start=2):
        try:
            subnet_id = None
            if row.get('subnet') and '(' in row['subnet'] and ')' in row['subnet']:
                cidr = row['subnet'].split('(')[1].split(')')[0]
                subnet_res = await db.execute(select(Subnet).where(Subnet.cidr == cidr))
                subnet = subnet_res.scalar_one_or_none()
                if subnet:
                    subnet_id = subnet.id
                else:
                    errors.append(f"Row {row_num}: Subnet with CIDR {cidr} not found")
                    continue
            else:
                errors.append(f"Row {row_num}: Invalid subnet format")
                continue
            
            device_id = None
            if row.get('device'):
                device_res = await db.execute(select(Device).where(Device.name == row['device']))
                device = device_res.scalar_one_or_none()
                if device:
                    device_id = device.id
            
            ip_address = row['ip_address'].strip()
            if not ip_in_cidr(ip_address, subnet.cidr) or not is_usable_ip_in_subnet(ip_address, subnet.cidr):
                errors.append(f"Row {row_num}: IP {ip_address} not valid for subnet {subnet.cidr}")
                continue
            
            if subnet.gateway_ip and ip_address == subnet.gateway_ip:
                errors.append(f"Row {row_num}: IP {ip_address} cannot be gateway")
                continue
            
            existing = await db.execute(
                select(IpAssignment).where(
                    IpAssignment.subnet_id == subnet_id,
                    IpAssignment.ip_address == ip_address
                )
            )
            if existing.scalar_one_or_none():
                errors.append(f"Row {row_num}: IP {ip_address} already assigned in subnet")
                continue
            
            ip_assignment = IpAssignment(
                subnet_id=subnet_id,
                device_id=device_id,
                ip_address=ip_address,
                interface=row.get('interface') or None,
                role=row.get('role') or None
            )
            db.add(ip_assignment)
            imported_count += 1
            
        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")
    
    if imported_count > 0:
        await db.commit()
    
    return {
        "imported_count": imported_count,
        "errors": errors
    }
