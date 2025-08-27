import ipaddress
import math
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.subnet import Subnet
from app.db.models.supernet import Supernet


def hosts_to_prefix_length(host_count: int) -> int:
    """Convert required host count to subnet prefix length"""
    if host_count <= 0:
        raise ValueError("Host count must be positive")
    
    if host_count == 1:
        return 32  # Single host
    elif host_count == 2:
        return 31  # Point-to-point link
    else:
        total_addresses = host_count + 2
        prefix_length = 32 - math.ceil(math.log2(total_addresses))
        return max(1, min(30, prefix_length))


async def find_available_subnet(
    db: AsyncSession,
    supernet_cidr: str,
    prefix_length: int
) -> Optional[str]:
    """Find first available subnet of given prefix length within supernet"""
    supernet = ipaddress.ip_network(supernet_cidr, strict=False)
    
    result = await db.execute(select(Subnet))
    existing_subnets = [
        ipaddress.ip_network(subnet.cidr, strict=False) 
        for subnet in result.scalars().all()
    ]
    
    try:
        for subnet in supernet.subnets(new_prefix=prefix_length):
            overlaps = any(
                subnet.overlaps(existing) for existing in existing_subnets
            )
            if not overlaps:
                return str(subnet)
    except ValueError:
        return None
    
    return None


async def allocate_subnet_cidr(
    db: AsyncSession,
    allocation_mode: str,
    supernet_id: Optional[int] = None,
    manual_cidr: Optional[str] = None,
    subnet_mask: Optional[int] = None,
    host_count: Optional[int] = None
) -> str:
    """Allocate subnet CIDR based on allocation mode"""
    
    if allocation_mode == "manual":
        if not manual_cidr:
            raise ValueError("Manual CIDR required for manual allocation mode")
        return manual_cidr
    
    if not supernet_id:
        raise ValueError("Supernet ID required for auto allocation modes")
    
    result = await db.execute(select(Supernet).where(Supernet.id == supernet_id))
    supernet = result.scalar_one_or_none()
    if not supernet:
        raise ValueError("Supernet not found")
    
    if allocation_mode == "auto_mask":
        if not subnet_mask:
            raise ValueError("Subnet mask required for auto mask allocation mode")
        allocated_cidr = await find_available_subnet(db, supernet.cidr, subnet_mask)
        
    elif allocation_mode == "auto_hosts":
        if not host_count:
            raise ValueError("Host count required for auto hosts allocation mode")
        prefix_length = hosts_to_prefix_length(host_count)
        allocated_cidr = await find_available_subnet(db, supernet.cidr, prefix_length)
        
    else:
        raise ValueError(f"Invalid allocation mode: {allocation_mode}")
    
    if not allocated_cidr:
        raise ValueError("No available subnet found in supernet")
    
    return allocated_cidr


def calculate_gateway_ip(cidr: str, gateway_mode: str) -> Optional[str]:
    """Calculate gateway IP based on gateway assignment mode"""
    if gateway_mode == "none":
        return None
    elif gateway_mode == "manual":
        return None
    elif gateway_mode == "auto_first":
        network = ipaddress.ip_network(cidr, strict=False)
        if network.prefixlen == 32:
            return str(network.network_address)
        elif network.prefixlen == 31:
            return str(network.network_address)
        else:
            return str(network.network_address + 1)
    else:
        raise ValueError(f"Invalid gateway mode: {gateway_mode}")
