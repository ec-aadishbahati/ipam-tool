from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models import Subnet, Vlan, Device, Supernet, Purpose

router = APIRouter()


@router.get("")
async def search(
    q: str = Query(""),
    site: str | None = None,
    environment: str | None = None,
    purpose_id: str | None = None,
    category_id: str | None = None,
    vlan_id: str | None = None,
    assigned_to: str | None = None,
    has_gateway: str | None = None,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    purpose_id_int = int(purpose_id) if purpose_id and purpose_id.strip() else None
    category_id_int = int(category_id) if category_id and category_id.strip() else None
    vlan_id_int = int(vlan_id) if vlan_id and vlan_id.strip() else None
    has_gateway_bool = None if not has_gateway or not has_gateway.strip() else has_gateway.lower() == 'true'
    
    results = {"subnets": [], "vlans": [], "devices": [], "supernets": []}
    
    subnet_query = select(Subnet).options(
        selectinload(Subnet.supernet),
        selectinload(Subnet.purpose),
        selectinload(Subnet.vlan),
    )
    
    if q:
        subnet_query = subnet_query.where(Subnet.cidr.ilike(f"%{q}%") | Subnet.name.ilike(f"%{q}%"))
    if site:
        subnet_query = subnet_query.where(Subnet.site == site)
    if environment:
        subnet_query = subnet_query.where(Subnet.environment == environment)
    if purpose_id_int:
        subnet_query = subnet_query.where(Subnet.purpose_id == purpose_id_int)
    if category_id_int:
        subnet_query = subnet_query.join(Purpose, Subnet.purpose_id == Purpose.id).where(Purpose.category_id == category_id_int)
    if vlan_id_int:
        subnet_query = subnet_query.where(Subnet.vlan_id == vlan_id_int)
    if assigned_to:
        subnet_query = subnet_query.where(Subnet.assigned_to.ilike(f"%{assigned_to}%"))
    if has_gateway_bool is not None:
        if has_gateway_bool:
            subnet_query = subnet_query.where(Subnet.gateway_ip.isnot(None))
        else:
            subnet_query = subnet_query.where(Subnet.gateway_ip.is_(None))
    
    subnets = await db.execute(subnet_query)
    
    supernet_query = select(Supernet)
    if q:
        supernet_query = supernet_query.where(Supernet.cidr.ilike(f"%{q}%") | Supernet.name.ilike(f"%{q}%"))
    if site:
        supernet_query = supernet_query.where(Supernet.site == site)
    if environment:
        supernet_query = supernet_query.where(Supernet.environment == environment)
    
    supernets = await db.execute(supernet_query)
    
    vlan_query = select(Vlan).options(selectinload(Vlan.purpose))
    if q:
        vlan_query = vlan_query.where(Vlan.name.ilike(f"%{q}%"))
    if site:
        vlan_query = vlan_query.where(Vlan.site == site)
    if environment:
        vlan_query = vlan_query.where(Vlan.environment == environment)
    if purpose_id_int:
        vlan_query = vlan_query.where(Vlan.purpose_id == purpose_id_int)
    if category_id_int:
        vlan_query = vlan_query.join(Purpose, Vlan.purpose_id == Purpose.id).where(Purpose.category_id == category_id_int)
    
    vlans = await db.execute(vlan_query)
    
    device_query = select(Device)
    if q:
        device_query = device_query.where(Device.name.ilike(f"%{q}%") | Device.hostname.ilike(f"%{q}%"))
    
    devices = await db.execute(device_query)
    
    results["subnets"] = [{"id": s.id, "cidr": s.cidr, "name": s.name, "site": s.site, "environment": s.environment} for s in subnets.scalars().all()]
    results["supernets"] = [{"id": s.id, "cidr": s.cidr, "name": s.name, "site": s.site, "environment": s.environment} for s in supernets.scalars().all()]
    results["vlans"] = [{"id": v.id, "vlan_id": v.vlan_id, "name": v.name, "site": v.site, "environment": v.environment} for v in vlans.scalars().all()]
    results["devices"] = [{"id": d.id, "name": d.name, "hostname": d.hostname} for d in devices.scalars().all()]
    return results
