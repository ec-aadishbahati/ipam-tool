from fastapi import APIRouter, Depends, HTTPException, UploadFile, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from sqlalchemy.orm import selectinload
from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models import Device
from app.schemas.device import DeviceCreate, DeviceOut, DeviceUpdate
from app.schemas.pagination import PaginatedResponse
from app.schemas.bulk import BulkDeleteRequest, BulkDeleteResponse, BulkExportRequest
from app.services.audit import record_audit

router = APIRouter()


@router.get("", response_model=PaginatedResponse[DeviceOut])
async def list_devices(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(75, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db), 
    user=Depends(get_current_user)
):
    count_result = await db.execute(select(func.count(Device.id)))
    total = count_result.scalar()
    
    offset = (page - 1) * limit
    res = await db.execute(
        select(Device).options(selectinload(Device.vlan)).order_by(Device.id.desc()).offset(offset).limit(limit)
    )
    devices = res.scalars().all()
    
    return PaginatedResponse.create(devices, total, page, limit)


@router.post("", response_model=DeviceOut)
async def create_device(payload: DeviceCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    obj = Device(
        name=payload.name,
        role=payload.role,
        hostname=payload.hostname,
        location=payload.location,
        vendor=payload.vendor,
        serial_number=payload.serial_number,
        vlan_id=payload.vlan_id,
        rack_id=payload.rack_id,
        rack_position=payload.rack_position,
    )
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
    before = {"name": obj.name, "role": obj.role, "hostname": obj.hostname, "location": obj.location, "vendor": obj.vendor, "serial_number": obj.serial_number, "vlan_id": obj.vlan_id, "rack_id": obj.rack_id, "rack_position": obj.rack_position}
    if payload.name is not None:
        obj.name = payload.name
    if payload.role is not None:
        obj.role = payload.role
    if payload.hostname is not None:
        obj.hostname = payload.hostname
    if payload.location is not None:
        obj.location = payload.location
    if payload.vendor is not None:
        obj.vendor = payload.vendor
    if payload.serial_number is not None:
        obj.serial_number = payload.serial_number
    if payload.vlan_id is not None:
        obj.vlan_id = payload.vlan_id
    if payload.rack_id is not None:
        obj.rack_id = payload.rack_id
    if payload.rack_position is not None:
        obj.rack_position = payload.rack_position
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    after = {"name": obj.name, "role": obj.role, "hostname": obj.hostname, "location": obj.location, "vendor": obj.vendor, "serial_number": obj.serial_number, "vlan_id": obj.vlan_id, "rack_id": obj.rack_id, "rack_position": obj.rack_position}
    await record_audit(db, entity_type="device", entity_id=obj.id, action="update", before=before, after=after, user_id=user.id)
    return obj


@router.delete("/bulk")
async def bulk_delete_devices(payload: BulkDeleteRequest, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    deleted_count = 0
    errors = []
    
    for device_id in payload.ids:
        try:
            result = await db.execute(select(Device).where(Device.id == device_id))
            device = result.scalar_one_or_none()
            if device:
                await db.execute(delete(Device).where(Device.id == device_id))
                await record_audit(db, entity_type="device", entity_id=device_id, action="bulk_delete", before=None, after=None, user_id=user.id)
                deleted_count += 1
            else:
                errors.append(f"Device with ID {device_id} not found")
        except Exception as e:
            errors.append(f"Failed to delete device {device_id}: {str(e)}")
    
    if deleted_count > 0:
        await db.commit()
    
    return BulkDeleteResponse(deleted_count=deleted_count, errors=errors)


@router.delete("/{device_id}")
async def delete_device(device_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    await db.execute(delete(Device).where(Device.id == device_id))
    await db.commit()
    await record_audit(db, entity_type="device", entity_id=device_id, action="delete", before=None, after=None, user_id=user.id)
    return {"message": "deleted"}


@router.get("/export/csv")
async def export_devices_csv(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    from app.utils.csv_export import create_csv_response
    
    res = await db.execute(select(Device).options(selectinload(Device.vlan), selectinload(Device.rack)))
    devices = res.scalars().all()
    
    data = []
    for device in devices:
        data.append({
            "name": device.name or "",
            "hostname": device.hostname or "",
            "role": device.role or "",
            "location": device.location or "",
            "vendor": device.vendor or "",
            "serial_number": device.serial_number or "",
            "vlan": f"{device.vlan.vlan_id} - {device.vlan.name}" if device.vlan else "",
            "rack": device.rack.name if device.rack else "",
            "rack_position": str(device.rack_position) if device.rack_position else ""
        })
    
    headers = ["name", "hostname", "role", "location", "vendor", "serial_number", "vlan", "rack", "rack_position"]
    return create_csv_response(data, headers, "devices.csv")


@router.get("/import/template")
async def get_device_import_template():
    from app.utils.csv_export import create_csv_template
    
    headers = ["name", "hostname", "role", "location", "vendor", "serial_number", "ip_address", "interface", "vlan", "rack", "rack_position"]
    sample_data = ["Server-01", "srv01.example.com", "Web Server", "Rack A1", "Cisco", "ABC123456789", "10.1.0.10", "eth0", "100 - Production", "Rack-01", "1"]
    return create_csv_template(headers, sample_data, "device_import_template.csv")


@router.post("/import/csv")
async def import_devices_csv(file: UploadFile, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    import csv
    import io
    from app.db.models import Vlan, Rack, Subnet, IpAssignment
    from app.services.ipam import ip_in_cidr
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    content = await file.read()
    csv_data = io.StringIO(content.decode('utf-8'))
    reader = csv.DictReader(csv_data)
    
    imported_count = 0
    errors = []
    
    for row_num, row in enumerate(reader, start=2):
        try:
            existing = await db.execute(select(Device).where(Device.name == row['name']))
            if existing.scalar_one_or_none():
                errors.append(f"Row {row_num}: Device with name {row['name']} already exists")
                continue
            
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
            
            rack_id = None
            if row.get('rack'):
                rack_res = await db.execute(select(Rack).where(Rack.name == row['rack']))
                rack = rack_res.scalar_one_or_none()
                if rack:
                    rack_id = rack.id
            
            rack_position = None
            if row.get('rack_position'):
                try:
                    rack_position = int(row['rack_position'])
                except ValueError:
                    pass
            
            device = Device(
                name=row['name'],
                hostname=row.get('hostname') or None,
                role=row.get('role') or None,
                location=row.get('location') or None,
                vendor=row.get('vendor') or None,
                serial_number=row.get('serial_number') or None,
                vlan_id=vlan_id,
                rack_id=rack_id,
                rack_position=rack_position,
            )
            
            db.add(device)
            await db.flush()
            
            if row.get('ip_address'):
                ip_address = row['ip_address'].strip()
                if ip_address:
                    subnets_res = await db.execute(select(Subnet))
                    subnets = subnets_res.scalars().all()
                    
                    matching_subnet = None
                    for subnet in subnets:
                        if ip_in_cidr(ip_address, subnet.cidr):
                            matching_subnet = subnet
                            break
                    
                    if matching_subnet:
                        existing_ip = await db.execute(
                            select(IpAssignment).where(
                                IpAssignment.subnet_id == matching_subnet.id,
                                IpAssignment.ip_address == ip_address
                            )
                        )
                        if not existing_ip.scalar_one_or_none():
                            ip_assignment = IpAssignment(
                                subnet_id=matching_subnet.id,
                                device_id=device.id,
                                ip_address=ip_address,
                                interface=row.get('interface') or None,
                                role="Device IP"
                            )
                            db.add(ip_assignment)
                        else:
                            errors.append(f"Row {row_num}: IP address {ip_address} already assigned")
                    else:
                        errors.append(f"Row {row_num}: No subnet found for IP address {ip_address}")
            
            imported_count += 1
            
        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")
    
    if imported_count > 0:
        await db.commit()
    
    return {
        "imported_count": imported_count,
        "errors": errors
    }




@router.post("/export/selected")
async def export_selected_devices(payload: BulkExportRequest, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    from app.utils.csv_export import create_csv_response
    
    res = await db.execute(
        select(Device).options(selectinload(Device.vlan), selectinload(Device.rack))
        .where(Device.id.in_(payload.ids))
    )
    devices = res.scalars().all()
    
    data = []
    for device in devices:
        data.append({
            "name": device.name or "",
            "hostname": device.hostname or "",
            "role": device.role or "",
            "location": device.location or "",
            "vendor": device.vendor or "",
            "serial_number": device.serial_number or "",
            "vlan": f"{device.vlan.vlan_id} - {device.vlan.name}" if device.vlan else "",
            "rack": device.rack.name if device.rack else "",
            "rack_position": str(device.rack_position) if device.rack_position else ""
        })
    
    headers = ["name", "hostname", "role", "location", "vendor", "serial_number", "vlan", "rack", "rack_position"]
    return create_csv_response(data, headers, "devices-selected.csv")
