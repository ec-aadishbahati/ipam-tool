from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models import Subnet, Vlan, Device

router = APIRouter()


@router.get("")
async def search(
    q: str = Query(""),
    site: str | None = None,
    environment: str | None = None,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    results = {"subnets": [], "vlans": [], "devices": []}
    if q:
        subnets = await db.execute(select(Subnet).where(Subnet.cidr.ilike(f"%{q}%") | Subnet.name.ilike(f"%{q}%")))
        vlans = await db.execute(select(Vlan).where(Vlan.name.ilike(f"%{q}%")))
        devices = await db.execute(select(Device).where(Device.name.ilike(f"%{q}%") | Device.hostname.ilike(f"%{q}%")))
    else:
        subnets = await db.execute(select(Subnet))
        vlans = await db.execute(select(Vlan))
        devices = await db.execute(select(Device))
    srows = [s for s in subnets.scalars().all() if (site is None or s.site == site) and (environment is None or s.environment == environment)]
    vrows = [v for v in vlans.scalars().all() if (site is None or v.site == site) and (environment is None or v.environment == environment)]
    drows = devices.scalars().all()
    results["subnets"] = [{"id": s.id, "cidr": s.cidr, "name": s.name} for s in srows]
    results["vlans"] = [{"id": v.id, "vlan_id": v.vlan_id, "name": v.name, "site": v.site, "environment": v.environment} for v in vrows]
    results["devices"] = [{"id": d.id, "name": d.name, "hostname": d.hostname} for d in drows]
    return results
