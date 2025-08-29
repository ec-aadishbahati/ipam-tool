from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models import (
    Supernet, Subnet, Device, Rack, Purpose, Vlan, AuditLog, IpAssignment
)
from app.utils.csv_export import create_excel_response

router = APIRouter()


@router.get("/all")
async def export_all_data(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    worksheets = {}
    
    supernet_count = await db.scalar(select(func.count(Supernet.id)))
    subnet_count = await db.scalar(select(func.count(Subnet.id)))
    device_count = await db.scalar(select(func.count(Device.id)))
    rack_count = await db.scalar(select(func.count(Rack.id)))
    vlan_count = await db.scalar(select(func.count(Vlan.id)))
    ip_assignment_count = await db.scalar(select(func.count(IpAssignment.id)))
    
    worksheets["Dashboard"] = {
        "headers": ["Metric", "Count"],
        "data": [
            {"Metric": "Total Supernets", "Count": supernet_count or 0},
            {"Metric": "Total Subnets", "Count": subnet_count or 0},
            {"Metric": "Total Devices", "Count": device_count or 0},
            {"Metric": "Total Racks", "Count": rack_count or 0},
            {"Metric": "Total VLANs", "Count": vlan_count or 0},
            {"Metric": "Total IP Assignments", "Count": ip_assignment_count or 0},
        ]
    }
    
    supernets_res = await db.execute(select(Supernet))
    supernets = supernets_res.scalars().all()
    worksheets["Supernets"] = {
        "headers": ["name", "cidr", "site", "environment"],
        "data": [
            {
                "name": s.name or "",
                "cidr": s.cidr,
                "site": s.site or "",
                "environment": s.environment or ""
            }
            for s in supernets
        ]
    }
    
    subnets_res = await db.execute(
        select(Subnet).options(
            selectinload(Subnet.purpose),
            selectinload(Subnet.vlan)
        )
    )
    subnets = subnets_res.scalars().all()
    worksheets["Subnets"] = {
        "headers": ["name", "cidr", "purpose", "assigned_to", "gateway_ip", "vlan", "site", "environment"],
        "data": [
            {
                "name": s.name or "",
                "cidr": s.cidr,
                "purpose": s.purpose.name if s.purpose else "",
                "assigned_to": s.assigned_to or "",
                "gateway_ip": s.gateway_ip or "",
                "vlan": f"{s.vlan.vlan_id} - {s.vlan.name}" if s.vlan else "",
                "site": s.site or "",
                "environment": s.environment or ""
            }
            for s in subnets
        ]
    }
    
    devices_res = await db.execute(
        select(Device).options(
            selectinload(Device.vlan),
            selectinload(Device.rack)
        )
    )
    devices = devices_res.scalars().all()
    worksheets["Devices"] = {
        "headers": ["name", "hostname", "role", "location", "vendor", "serial_number", "vlan", "rack", "rack_position"],
        "data": [
            {
                "name": d.name or "",
                "hostname": d.hostname or "",
                "role": d.role or "",
                "location": d.location or "",
                "vendor": d.vendor or "",
                "serial_number": d.serial_number or "",
                "vlan": f"{d.vlan.vlan_id} - {d.vlan.name}" if d.vlan else "",
                "rack": f"{d.rack.aisle}-{d.rack.rack_number}" if d.rack else "",
                "rack_position": str(d.rack_position) if d.rack_position else ""
            }
            for d in devices
        ]
    }
    
    racks_res = await db.execute(select(Rack))
    racks = racks_res.scalars().all()
    worksheets["Racks"] = {
        "headers": ["aisle", "rack_number", "position_count", "power_type", "power_capacity", "cooling_type", "location", "notes"],
        "data": [
            {
                "aisle": r.aisle,
                "rack_number": r.rack_number,
                "position_count": str(r.position_count),
                "power_type": r.power_type or "",
                "power_capacity": r.power_capacity or "",
                "cooling_type": r.cooling_type or "",
                "location": r.location or "",
                "notes": r.notes or ""
            }
            for r in racks
        ]
    }
    
    ip_assignments_res = await db.execute(
        select(IpAssignment).options(
            selectinload(IpAssignment.subnet),
            selectinload(IpAssignment.device)
        )
    )
    ip_assignments = ip_assignments_res.scalars().all()
    worksheets["IP Assignments"] = {
        "headers": ["subnet", "device", "ip_address", "role"],
        "data": [
            {
                "subnet": f"{ip.subnet.name} ({ip.subnet.cidr})" if ip.subnet else "",
                "device": ip.device.name if ip.device else "",
                "ip_address": ip.ip_address,
                "role": ip.role or ""
            }
            for ip in ip_assignments
        ]
    }
    
    vlans_res = await db.execute(
        select(Vlan).options(selectinload(Vlan.purpose))
    )
    vlans = vlans_res.scalars().all()
    worksheets["VLANs"] = {
        "headers": ["site", "environment", "vlan_id", "name", "purpose"],
        "data": [
            {
                "site": v.site,
                "environment": v.environment,
                "vlan_id": str(v.vlan_id),
                "name": v.name,
                "purpose": v.purpose.name if v.purpose else ""
            }
            for v in vlans
        ]
    }
    
    purposes_res = await db.execute(select(Purpose).order_by(Purpose.name))
    purposes = purposes_res.scalars().all()
    worksheets["Purposes"] = {
        "headers": ["name", "description", "category"],
        "data": [
            {
                "name": p.name,
                "description": p.description or "",
                "category": p.category or ""
            }
            for p in purposes
        ]
    }
    
    audits_res = await db.execute(
        select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(200)
    )
    audits = audits_res.scalars().all()
    worksheets["Audits"] = {
        "headers": ["entity_type", "entity_id", "action", "user_id", "timestamp"],
        "data": [
            {
                "entity_type": a.entity_type,
                "entity_id": str(a.entity_id),
                "action": a.action,
                "user_id": str(a.user_id) if a.user_id else "",
                "timestamp": str(a.timestamp)
            }
            for a in audits
        ]
    }
    
    return create_excel_response(worksheets, "ee_spark_export.xlsx")
