from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models import IpAssignment, Subnet
from app.schemas.ip_assignment import IpAssignmentCreate, IpAssignmentOut, IpAssignmentUpdate
from app.services.ipam import ip_in_cidr, is_usable_ip_in_subnet
from app.services.audit import record_audit

router = APIRouter()


@router.get("", response_model=list[IpAssignmentOut])
async def list_ip_assignments(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    res = await db.execute(select(IpAssignment))
    return res.scalars().all()


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
    obj = IpAssignment(subnet_id=payload.subnet_id, device_id=payload.device_id, ip_address=payload.ip_address, role=payload.role)
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
    before = {"device_id": obj.device_id, "ip_address": obj.ip_address, "role": obj.role}
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
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    after = {"device_id": obj.device_id, "ip_address": obj.ip_address, "role": obj.role}
    await record_audit(db, entity_type="ip_assignment", entity_id=obj.id, action="update", before=before, after=after, user_id=user.id)
    return obj


@router.delete("/{assignment_id}")
async def delete_ip_assignment(assignment_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    await db.execute(delete(IpAssignment).where(IpAssignment.id == assignment_id))
    await db.commit()
    await record_audit(db, entity_type="ip_assignment", entity_id=assignment_id, action="delete", before=None, after=None, user_id=user.id)
    return {"message": "deleted"}
