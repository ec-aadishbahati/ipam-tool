import ipaddress
from typing import Any
from pydantic import validator


def validate_cidr_format(cidr: str) -> str:
    """Validate CIDR notation format (e.g., '192.168.1.0/24')"""
    try:
        network = ipaddress.ip_network(cidr, strict=False)
        return str(network)
    except (ipaddress.AddressValueError, ValueError) as e:
        raise ValueError(f"Invalid CIDR format: {cidr}. {str(e)}")


def validate_ip_address_format(ip: str) -> str:
    """Validate IP address format (e.g., '192.168.1.1')"""
    try:
        addr = ipaddress.ip_address(ip)
        return str(addr)
    except (ipaddress.AddressValueError, ValueError) as e:
        raise ValueError(f"Invalid IP address format: {ip}. {str(e)}")


def validate_ip_in_cidr(ip: str, cidr: str) -> bool:
    """Validate that IP address is within the given CIDR range"""
    try:
        addr = ipaddress.ip_address(ip)
        network = ipaddress.ip_network(cidr, strict=False)
        return addr in network
    except (ipaddress.AddressValueError, ValueError):
        return False


def validate_gateway_in_subnet(gateway: str, cidr: str) -> bool:
    """Validate that gateway IP is within subnet and usable"""
    try:
        network = ipaddress.ip_network(cidr, strict=False)
        addr = ipaddress.ip_address(gateway)
        
        if network.prefixlen == network.max_prefixlen:
            return addr in network
        
        return addr in list(network.hosts())
    except (ipaddress.AddressValueError, ValueError):
        return False


def create_cidr_validator(field_name: str = 'cidr'):
    """Create a Pydantic validator for CIDR fields"""
    def cidr_validator(cls, v):
        if v is None:
            return v
        return validate_cidr_format(v)
    
    return validator(field_name, allow_reuse=True)(cidr_validator)


def create_ip_validator(field_name: str = 'ip'):
    """Create a Pydantic validator for IP address fields"""
    def ip_validator(cls, v):
        if v is None:
            return v
        return validate_ip_address_format(v)
    
    return validator(field_name, allow_reuse=True)(ip_validator)


def create_gateway_validator(cidr_field: str = 'cidr'):
    """Create a Pydantic validator for gateway IP that checks against CIDR"""
    def gateway_validator(cls, v, values):
        if v is None:
            return v
        
        validate_ip_address_format(v)
        
        cidr = values.get(cidr_field)
        if cidr and not validate_gateway_in_subnet(v, cidr):
            raise ValueError(f"Gateway IP {v} is not usable within subnet {cidr}")
        
        return v
    
    return validator('gateway_ip', allow_reuse=True)(gateway_validator)
