import ipaddress


def cidr_overlap(cidr_a: str, cidr_b: str) -> bool:
    net_a = ipaddress.ip_network(cidr_a, strict=False)
    net_b = ipaddress.ip_network(cidr_b, strict=False)
    return net_a.overlaps(net_b)


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


def calculate_subnet_utilization(cidr: str, assigned_ips: list[str]) -> float:
    """Calculate utilization percentage for a subnet"""
    network = ipaddress.ip_network(cidr, strict=False)
    if network.prefixlen == network.max_prefixlen:
        total_usable = 1
    elif network.prefixlen == 31:
        total_usable = 2
    else:
        total_usable = len(list(network.hosts()))
    
    if total_usable == 0:
        return 0.0
    
    return (len(assigned_ips) / total_usable) * 100


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
