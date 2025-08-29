import ipaddress
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession


def cidr_overlap(cidr_a: str, cidr_b: str) -> bool:
    net_a = ipaddress.ip_network(cidr_a, strict=False)
    net_b = ipaddress.ip_network(cidr_b, strict=False)
    return net_a.overlaps(net_b)


def cidr_contains(supernet_cidr: str, subnet_cidr: str) -> bool:
    """Check if supernet contains subnet (subnet is within supernet)"""
    try:
        supernet = ipaddress.ip_network(supernet_cidr, strict=False)
        subnet = ipaddress.ip_network(subnet_cidr, strict=False)
        return subnet.subnet_of(supernet)
    except (ValueError, TypeError):
        return False


def ip_in_cidr(ip: str, cidr: str) -> bool:
    return ipaddress.ip_address(ip) in ipaddress.ip_network(cidr, strict=False)


def is_usable_ip_in_subnet(ip: str, cidr: str) -> bool:
    net = ipaddress.ip_network(cidr, strict=False)
    addr = ipaddress.ip_address(ip)
    if net.prefixlen == net.max_prefixlen:
        return addr in net
    return addr in list(net.hosts())


def is_gateway_valid(gateway: str, cidr: str) -> bool:
    net = ipaddress.ip_network(cidr, strict=False)
    addr = ipaddress.ip_address(gateway)
    return addr in net and (net.prefixlen == net.max_prefixlen or addr in list(net.hosts()))


def get_usable_address_count(network: ipaddress._BaseNetwork) -> int:
    """Get count of usable IP addresses in a network, optimized for performance"""
    if network.prefixlen == network.max_prefixlen:
        return 1
    elif network.version == 4 and network.prefixlen == 31:
        return 2
    elif network.version == 6 and network.prefixlen == 127:
        return 2
    
    if network.version == 4:
        return network.num_addresses - 2
    else:
        return network.num_addresses


def calculate_subnet_utilization(cidr: str, assigned_ips: list[str]) -> float:
    """Calculate utilization percentage for a subnet"""
    network = ipaddress.ip_network(cidr, strict=False)
    total_usable = get_usable_address_count(network)
    
    if total_usable == 0:
        return 0.0
    
    return (len(assigned_ips) / total_usable) * 100


async def calculate_supernet_utilization(subnets: Sequence, db: AsyncSession) -> float:
    """
    Calculate supernet utilization percentage based on allocated subnet space.
    Uses bulk queries for performance optimization.
    """
    if not subnets:
        return 0.0
    
    supernet_cidr = None
    for subnet in subnets:
        if subnet.supernet:
            supernet_cidr = subnet.supernet.cidr
            break
    
    if not supernet_cidr:
        return 0.0
    
    supernet_network = ipaddress.ip_network(supernet_cidr, strict=False)
    total_supernet_ips = get_usable_address_count(supernet_network)
    
    if total_supernet_ips == 0:
        return 0.0
    
    total_allocated_ips = 0
    
    for subnet in subnets:
        subnet_network = ipaddress.ip_network(subnet.cidr, strict=False)
        subnet_ips = get_usable_address_count(subnet_network)
        total_allocated_ips += subnet_ips
    
    return (total_allocated_ips / total_supernet_ips) * 100


def get_valid_ip_range(cidr: str) -> tuple[str, str]:
    """Get first and last valid IP addresses in subnet (excluding network/broadcast)"""
    network = ipaddress.ip_network(cidr, strict=False)
    if network.prefixlen == network.max_prefixlen:
        return str(network.network_address), str(network.network_address)
    elif network.prefixlen == 31:
        return str(network.network_address), str(network.broadcast_address)
    else:
        hosts = list(network.hosts())
        return str(hosts[0]), str(hosts[-1])
