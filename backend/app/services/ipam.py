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
    return addr in net.hosts()


def is_gateway_valid(gateway: str, cidr: str) -> bool:
    net = ipaddress.ip_network(cidr, strict=False)
    addr = ipaddress.ip_address(gateway)
    return addr in net and (net.prefixlen == net.max_prefixlen or addr in net.hosts())
