import json
import os
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, text
from sqlalchemy.orm import selectinload

from app.db.models import (
    User, Category, Purpose, Rack, Supernet, Vlan, 
    Subnet, Device, IpAssignment
)
from app.schemas.backup import BackupFile, BackupMetadata, BackupData, BackupListItem, RestoreResult


BACKUP_DIR = Path("Backup")
BACKUP_VERSION = "1.0"


async def create_backup(db: AsyncSession, user_id: int) -> str:
    """Create a complete backup of all system data"""
    print(f"DEBUG: Starting backup creation for user_id: {user_id}")
    backup_id = str(uuid.uuid4())
    timestamp = datetime.utcnow()
    print(f"DEBUG: Generated backup_id: {backup_id}")
    
    print("DEBUG: Querying users...")
    users_result = await db.execute(select(User))
    users = users_result.scalars().all()
    print(f"DEBUG: Found {len(users)} users")
    
    print("DEBUG: Querying categories...")
    categories_result = await db.execute(select(Category))
    categories = categories_result.scalars().all()
    print(f"DEBUG: Found {len(categories)} categories")
    
    print("DEBUG: Querying purposes...")
    purposes_result = await db.execute(
        select(Purpose).options(selectinload(Purpose.category))
    )
    purposes = purposes_result.scalars().all()
    print(f"DEBUG: Found {len(purposes)} purposes")
    
    print("DEBUG: Querying racks...")
    racks_result = await db.execute(select(Rack))
    racks = racks_result.scalars().all()
    print(f"DEBUG: Found {len(racks)} racks")
    
    print("DEBUG: Querying supernets...")
    supernets_result = await db.execute(select(Supernet))
    supernets = supernets_result.scalars().all()
    print(f"DEBUG: Found {len(supernets)} supernets")
    
    print("DEBUG: Querying vlans...")
    vlans_result = await db.execute(
        select(Vlan).options(selectinload(Vlan.purpose))
    )
    vlans = vlans_result.scalars().all()
    print(f"DEBUG: Found {len(vlans)} vlans")
    
    print("DEBUG: Querying subnets...")
    subnets_result = await db.execute(
        select(Subnet).options(
            selectinload(Subnet.purpose),
            selectinload(Subnet.vlan),
            selectinload(Subnet.supernet)
        )
    )
    subnets = subnets_result.scalars().all()
    print(f"DEBUG: Found {len(subnets)} subnets")
    
    print("DEBUG: Querying devices...")
    devices_result = await db.execute(
        select(Device).options(
            selectinload(Device.vlan),
            selectinload(Device.rack)
        )
    )
    devices = devices_result.scalars().all()
    print(f"DEBUG: Found {len(devices)} devices")
    
    print("DEBUG: Querying ip_assignments...")
    ip_assignments_result = await db.execute(
        select(IpAssignment).options(
            selectinload(IpAssignment.subnet),
            selectinload(IpAssignment.device)
        )
    )
    ip_assignments = ip_assignments_result.scalars().all()
    print(f"DEBUG: Found {len(ip_assignments)} ip_assignments")
    
    print("DEBUG: Starting data serialization...")
    try:
        users_data = [_serialize_user(user) for user in users]
        print("DEBUG: Users serialized")
    except Exception as e:
        print(f"DEBUG: Error serializing users: {e}")
        raise
    
    try:
        categories_data = [_serialize_category(category) for category in categories]
        print("DEBUG: Categories serialized")
    except Exception as e:
        print(f"DEBUG: Error serializing categories: {e}")
        raise
    
    try:
        purposes_data = [_serialize_purpose(purpose) for purpose in purposes]
        print("DEBUG: Purposes serialized")
    except Exception as e:
        print(f"DEBUG: Error serializing purposes: {e}")
        raise
    try:
        racks_data = [_serialize_rack(rack) for rack in racks]
        print("DEBUG: Racks serialized")
    except Exception as e:
        print(f"DEBUG: Error serializing racks: {e}")
        raise
    
    try:
        supernets_data = [_serialize_supernet(supernet) for supernet in supernets]
        print("DEBUG: Supernets serialized")
    except Exception as e:
        print(f"DEBUG: Error serializing supernets: {e}")
        raise
    
    try:
        vlans_data = [_serialize_vlan(vlan) for vlan in vlans]
        print("DEBUG: VLANs serialized")
    except Exception as e:
        print(f"DEBUG: Error serializing vlans: {e}")
        raise
    try:
        subnets_data = [_serialize_subnet(subnet) for subnet in subnets]
        print("DEBUG: Subnets serialized")
    except Exception as e:
        print(f"DEBUG: Error serializing subnets: {e}")
        raise
    
    try:
        devices_data = [_serialize_device(device) for device in devices]
        print("DEBUG: Devices serialized")
    except Exception as e:
        print(f"DEBUG: Error serializing devices: {e}")
        raise
    
    try:
        ip_assignments_data = [_serialize_ip_assignment(ip) for ip in ip_assignments]
        print("DEBUG: IP assignments serialized")
    except Exception as e:
        print(f"DEBUG: Error serializing ip_assignments: {e}")
        raise
    
    total_records = (
        len(users_data) + len(categories_data) + len(purposes_data) +
        len(racks_data) + len(supernets_data) + len(vlans_data) +
        len(subnets_data) + len(devices_data) + len(ip_assignments_data)
    )
    
    backup_data = BackupFile(
        metadata=BackupMetadata(
            created_at=timestamp,
            version=BACKUP_VERSION,
            total_records=total_records,
            created_by_user_id=user_id,
            backup_id=backup_id
        ),
        data=BackupData(
            users=users_data,
            categories=categories_data,
            purposes=purposes_data,
            racks=racks_data,
            supernets=supernets_data,
            vlans=vlans_data,
            subnets=subnets_data,
            devices=devices_data,
            ip_assignments=ip_assignments_data
        )
    )
    
    filename = f"ipam_backup_{timestamp.strftime('%Y-%m-%d_%H-%M-%S')}.json"
    filepath = BACKUP_DIR / filename
    print(f"DEBUG: Creating backup file: {filepath}")
    
    BACKUP_DIR.mkdir(exist_ok=True)
    print("DEBUG: Backup directory created/verified")
    
    print("DEBUG: Writing backup file...")
    with open(filepath, 'w') as f:
        json.dump(backup_data.dict(), f, indent=2, default=str)
    print("DEBUG: Backup file written successfully")
    
    print(f"DEBUG: Backup creation completed, returning backup_id: {backup_id}")
    return backup_id


async def list_backups() -> List[BackupListItem]:
    """List all available backup files"""
    if not BACKUP_DIR.exists():
        return []
    
    backups = []
    for filepath in BACKUP_DIR.glob("*.json"):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                metadata = data.get('metadata', {})
                
                created_at_str = metadata.get('created_at', '')
                try:
                    created_at = datetime.fromisoformat(created_at_str)
                except ValueError:
                    try:
                        created_at = datetime.strptime(created_at_str, '%Y-%m-%d %H:%M:%S.%f')
                    except ValueError:
                        created_at = datetime.utcnow()
                
                backups.append(BackupListItem(
                    backup_id=metadata.get('backup_id', ''),
                    filename=filepath.name,
                    created_at=created_at,
                    size_bytes=filepath.stat().st_size,
                    total_records=metadata.get('total_records', 0),
                    created_by_user_id=metadata.get('created_by_user_id', 0)
                ))
        except Exception:
            continue
    
    return sorted(backups, key=lambda x: x.created_at, reverse=True)


async def restore_backup(db: AsyncSession, backup_data: Dict[str, Any]) -> RestoreResult:
    """Restore system from backup data with complete override"""
    try:
        if 'metadata' not in backup_data or 'data' not in backup_data:
            return RestoreResult(
                success=False,
                message="Invalid backup file structure",
                records_imported={}
            )
        
        data = backup_data['data']
        records_imported = {}
        
        await db.execute(delete(IpAssignment))
        await db.execute(delete(Device))
        await db.execute(delete(Subnet))
        await db.execute(delete(Vlan))
        await db.execute(delete(Supernet))
        await db.execute(delete(Rack))
        await db.execute(delete(Purpose))
        await db.execute(delete(Category))
        await db.execute(delete(User))
        
        await db.execute(text("DELETE FROM sqlite_sequence WHERE name IN ('users', 'categories', 'purposes', 'racks', 'supernets', 'vlans', 'subnets', 'devices', 'ip_assignments')"))
        await db.commit()
        
        users_count = 0
        for user_data in data.get('users', []):
            user = User(**_deserialize_user(user_data))
            db.add(user)
            users_count += 1
        await db.commit()
        records_imported['users'] = users_count
        
        categories_count = 0
        for category_data in data.get('categories', []):
            category = Category(**_deserialize_category(category_data))
            db.add(category)
            categories_count += 1
        await db.commit()
        records_imported['categories'] = categories_count
        
        purposes_count = 0
        for purpose_data in data.get('purposes', []):
            purpose_dict = _deserialize_purpose(purpose_data)
            
            if purpose_data.get('category_name'):
                category_result = await db.execute(
                    select(Category).where(Category.name == purpose_data['category_name'])
                )
                category = category_result.scalar_one_or_none()
                if category:
                    purpose_dict['category_id'] = category.id
            
            purpose = Purpose(**purpose_dict)
            db.add(purpose)
            purposes_count += 1
        await db.commit()
        records_imported['purposes'] = purposes_count
        
        racks_count = 0
        for rack_data in data.get('racks', []):
            rack = Rack(**_deserialize_rack(rack_data))
            db.add(rack)
            racks_count += 1
        await db.commit()
        records_imported['racks'] = racks_count
        
        supernets_count = 0
        for supernet_data in data.get('supernets', []):
            supernet = Supernet(**_deserialize_supernet(supernet_data))
            db.add(supernet)
            supernets_count += 1
        await db.commit()
        records_imported['supernets'] = supernets_count
        
        vlans_count = 0
        for vlan_data in data.get('vlans', []):
            vlan_dict = _deserialize_vlan(vlan_data)
            
            if vlan_data.get('purpose_name'):
                purpose_result = await db.execute(
                    select(Purpose).where(Purpose.name == vlan_data['purpose_name'])
                )
                purpose = purpose_result.scalar_one_or_none()
                if purpose:
                    vlan_dict['purpose_id'] = purpose.id
            
            vlan = Vlan(**vlan_dict)
            db.add(vlan)
            vlans_count += 1
        await db.commit()
        records_imported['vlans'] = vlans_count
        
        subnets_count = 0
        for subnet_data in data.get('subnets', []):
            subnet_dict = _deserialize_subnet(subnet_data)
            
            if subnet_data.get('purpose_name'):
                purpose_result = await db.execute(
                    select(Purpose).where(Purpose.name == subnet_data['purpose_name'])
                )
                purpose = purpose_result.scalar_one_or_none()
                if purpose:
                    subnet_dict['purpose_id'] = purpose.id
            
            if subnet_data.get('vlan_name'):
                vlan_result = await db.execute(
                    select(Vlan).where(Vlan.name == subnet_data['vlan_name'])
                )
                vlan = vlan_result.scalar_one_or_none()
                if vlan:
                    subnet_dict['vlan_id'] = vlan.id
            
            if subnet_data.get('supernet_cidr'):
                supernet_result = await db.execute(
                    select(Supernet).where(Supernet.cidr == subnet_data['supernet_cidr'])
                )
                supernet = supernet_result.scalar_one_or_none()
                if supernet:
                    subnet_dict['supernet_id'] = supernet.id
            
            subnet = Subnet(**subnet_dict)
            db.add(subnet)
            subnets_count += 1
        await db.commit()
        records_imported['subnets'] = subnets_count
        
        devices_count = 0
        for device_data in data.get('devices', []):
            device_dict = _deserialize_device(device_data)
            
            if device_data.get('vlan_name'):
                vlan_result = await db.execute(
                    select(Vlan).where(Vlan.name == device_data['vlan_name'])
                )
                vlan = vlan_result.scalar_one_or_none()
                if vlan:
                    device_dict['vlan_id'] = vlan.id
            
            if device_data.get('rack_name'):
                rack_result = await db.execute(
                    select(Rack).where(Rack.name == device_data['rack_name'])
                )
                rack = rack_result.scalar_one_or_none()
                if rack:
                    device_dict['rack_id'] = rack.id
            
            device = Device(**device_dict)
            db.add(device)
            devices_count += 1
        await db.commit()
        records_imported['devices'] = devices_count
        
        ip_assignments_count = 0
        for ip_data in data.get('ip_assignments', []):
            ip_dict = _deserialize_ip_assignment(ip_data)
            
            if ip_data.get('subnet_cidr'):
                subnet_result = await db.execute(
                    select(Subnet).where(Subnet.cidr == ip_data['subnet_cidr'])
                )
                subnet = subnet_result.scalar_one_or_none()
                if subnet:
                    ip_dict['subnet_id'] = subnet.id
            
            if ip_data.get('device_name'):
                device_result = await db.execute(
                    select(Device).where(Device.name == ip_data['device_name'])
                )
                device = device_result.scalar_one_or_none()
                if device:
                    ip_dict['device_id'] = device.id
            
            ip_assignment = IpAssignment(**ip_dict)
            db.add(ip_assignment)
            ip_assignments_count += 1
        await db.commit()
        records_imported['ip_assignments'] = ip_assignments_count
        
        return RestoreResult(
            success=True,
            message="Backup restored successfully",
            records_imported=records_imported
        )
        
    except Exception as e:
        await db.rollback()
        return RestoreResult(
            success=False,
            message=f"Restore failed: {str(e)}",
            records_imported={}
        )


def get_backup_file_path(backup_id: str) -> Optional[Path]:
    """Get file path for a backup by ID"""
    if not BACKUP_DIR.exists():
        return None
    
    for filepath in BACKUP_DIR.glob("*.json"):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                if data.get('metadata', {}).get('backup_id') == backup_id:
                    return filepath
        except Exception:
            continue
    
    return None


def delete_backup_file(backup_id: str) -> bool:
    """Delete a backup file by ID"""
    filepath = get_backup_file_path(backup_id)
    if filepath and filepath.exists():
        filepath.unlink()
        return True
    return False


def _serialize_user(user: User) -> Dict[str, Any]:
    return {
        'id': user.id,
        'email': user.email,
        'hashed_password': user.hashed_password,
        'is_admin': user.is_admin,
        'password_changed_at': user.password_changed_at.isoformat() if user.password_changed_at else None,
        'must_change_password': user.must_change_password
    }


def _serialize_category(category: Category) -> Dict[str, Any]:
    return {
        'id': category.id,
        'name': category.name,
        'description': category.description
    }


def _serialize_purpose(purpose: Purpose) -> Dict[str, Any]:
    return {
        'id': purpose.id,
        'name': purpose.name,
        'description': purpose.description,
        'category_id': purpose.category_id,
        'category_name': purpose.category.name if purpose.category else None
    }


def _serialize_rack(rack: Rack) -> Dict[str, Any]:
    return {
        'id': rack.id,
        'name': rack.name,
        'location': rack.location,
        'height': rack.height
    }


def _serialize_supernet(supernet: Supernet) -> Dict[str, Any]:
    return {
        'id': supernet.id,
        'name': supernet.name,
        'cidr': supernet.cidr,
        'site': supernet.site,
        'environment': supernet.environment,
    }


def _serialize_vlan(vlan: Vlan) -> Dict[str, Any]:
    return {
        'id': vlan.id,
        'vlan_id': vlan.vlan_id,
        'name': vlan.name,
        'site': vlan.site,
        'environment': vlan.environment,
        'purpose_id': vlan.purpose_id,
        'purpose_name': vlan.purpose.name if vlan.purpose else None
    }


def _serialize_subnet(subnet: Subnet) -> Dict[str, Any]:
    return {
        'id': subnet.id,
        'name': subnet.name,
        'cidr': subnet.cidr,
        'purpose_id': subnet.purpose_id,
        'purpose_name': subnet.purpose.name if subnet.purpose else None,
        'assigned_to': subnet.assigned_to,
        'gateway_ip': subnet.gateway_ip,
        'vlan_id': subnet.vlan_id,
        'vlan_name': subnet.vlan.name if subnet.vlan else None,
        'site': subnet.site,
        'environment': subnet.environment,
        'supernet_id': subnet.supernet_id,
        'supernet_cidr': subnet.supernet.cidr if subnet.supernet else None,
        'allocation_mode': subnet.allocation_mode,
        'gateway_mode': subnet.gateway_mode,
        'subnet_mask': subnet.subnet_mask,
        'host_count': subnet.host_count,
    }


def _serialize_device(device: Device) -> Dict[str, Any]:
    return {
        'id': device.id,
        'name': device.name,
        'role': device.role,
        'hostname': device.hostname,
        'location': device.location,
        'vendor': device.vendor,
        'serial_number': device.serial_number,
        'vlan_id': device.vlan_id,
        'vlan_name': device.vlan.name if device.vlan else None,
        'rack_id': device.rack_id,
        'rack_name': device.rack.name if device.rack else None,
        'rack_position': device.rack_position
    }


def _serialize_ip_assignment(ip: IpAssignment) -> Dict[str, Any]:
    return {
        'id': ip.id,
        'subnet_id': ip.subnet_id,
        'subnet_cidr': ip.subnet.cidr if ip.subnet else None,
        'device_id': ip.device_id,
        'device_name': ip.device.name if ip.device else None,
        'ip_address': ip.ip_address,
        'role': ip.role
    }


def _deserialize_user(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'email': data['email'],
        'hashed_password': data['hashed_password'],
        'is_admin': data.get('is_admin', False),
        'password_changed_at': datetime.fromisoformat(data['password_changed_at']) if data.get('password_changed_at') else datetime.utcnow(),
        'must_change_password': data.get('must_change_password', True)
    }


def _deserialize_category(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'name': data['name'],
        'description': data.get('description')
    }


def _deserialize_purpose(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'name': data['name'],
        'description': data.get('description'),
        'category_id': data.get('category_id')
    }


def _deserialize_rack(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'name': data['name'],
        'location': data.get('location'),
        'height': data.get('height')
    }


def _deserialize_supernet(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'name': data['name'],
        'cidr': data['cidr'],
        'site': data.get('site'),
        'environment': data.get('environment')
    }


def _deserialize_vlan(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'vlan_id': data['vlan_id'],
        'name': data['name'],
        'site': data.get('site'),
        'environment': data.get('environment'),
        'purpose_id': data.get('purpose_id')
    }


def _deserialize_subnet(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'name': data.get('name'),
        'cidr': data['cidr'],
        'purpose_id': data.get('purpose_id'),
        'assigned_to': data.get('assigned_to'),
        'gateway_ip': data.get('gateway_ip'),
        'vlan_id': data.get('vlan_id'),
        'site': data.get('site'),
        'environment': data.get('environment'),
        'supernet_id': data.get('supernet_id'),
        'allocation_mode': data.get('allocation_mode', 'manual'),
        'gateway_mode': data.get('gateway_mode', 'none'),
        'subnet_mask': data.get('subnet_mask'),
        'host_count': data.get('host_count')
    }


def _deserialize_device(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'name': data['name'],
        'role': data.get('role'),
        'hostname': data.get('hostname'),
        'location': data.get('location'),
        'vendor': data.get('vendor'),
        'serial_number': data.get('serial_number'),
        'vlan_id': data.get('vlan_id'),
        'rack_id': data.get('rack_id'),
        'rack_position': data.get('rack_position')
    }


def _deserialize_ip_assignment(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'subnet_id': data.get('subnet_id'),
        'device_id': data.get('device_id'),
        'ip_address': data['ip_address'],
        'role': data.get('role', 'Device IP')
    }
