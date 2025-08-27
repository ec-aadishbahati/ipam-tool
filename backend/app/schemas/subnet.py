from pydantic import BaseModel, validator
from app.core.validators import validate_cidr_format, validate_ip_address_format, validate_gateway_in_subnet


class SubnetBase(BaseModel):
    cidr: str | None = None
    name: str | None = None
    purpose_id: int | None = None
    assigned_to: str | None = None
    gateway_ip: str | None = None
    vlan_id: int | None = None
    site: str | None = None
    environment: str | None = None
    supernet_id: int | None = None
    
    allocation_mode: str = "manual"
    gateway_mode: str = "manual"
    subnet_mask: int | None = None
    host_count: int | None = None

    @validator('cidr')
    def validate_cidr(cls, v):
        if v is None:
            return v
        return validate_cidr_format(v)

    @validator('gateway_ip')
    def validate_gateway_ip(cls, v, values):
        if v is None:
            return v
        
        validate_ip_address_format(v)
        
        cidr = values.get('cidr')
        if cidr and not validate_gateway_in_subnet(v, cidr):
            raise ValueError(f"Gateway IP {v} is not usable within subnet {cidr}")
        
        return v

    @validator('allocation_mode')
    def validate_allocation_mode(cls, v):
        valid_modes = ["manual", "auto_mask", "auto_hosts"]
        if v not in valid_modes:
            raise ValueError(f"Invalid allocation mode. Must be one of: {valid_modes}")
        return v

    @validator('gateway_mode')
    def validate_gateway_mode(cls, v):
        valid_modes = ["manual", "auto_first", "none"]
        if v not in valid_modes:
            raise ValueError(f"Invalid gateway mode. Must be one of: {valid_modes}")
        return v


class SubnetCreate(SubnetBase):
    pass


class SubnetUpdate(BaseModel):
    cidr: str | None = None
    name: str | None = None
    purpose_id: int | None = None
    assigned_to: str | None = None
    gateway_ip: str | None = None
    vlan_id: int | None = None
    site: str | None = None
    environment: str | None = None
    supernet_id: int | None = None
    allocation_mode: str | None = None
    gateway_mode: str | None = None
    subnet_mask: int | None = None
    host_count: int | None = None

    @validator('cidr')
    def validate_cidr(cls, v):
        if v is None:
            return v
        return validate_cidr_format(v)

    @validator('gateway_ip')
    def validate_gateway_ip(cls, v, values):
        if v is None:
            return v
        
        validate_ip_address_format(v)
        
        cidr = values.get('cidr')
        if cidr and not validate_gateway_in_subnet(v, cidr):
            raise ValueError(f"Gateway IP {v} is not usable within subnet {cidr}")
        
        return v

    @validator('allocation_mode')
    def validate_allocation_mode(cls, v):
        if v is None:
            return v
        valid_modes = ["manual", "auto_mask", "auto_hosts"]
        if v not in valid_modes:
            raise ValueError(f"Invalid allocation mode. Must be one of: {valid_modes}")
        return v

    @validator('gateway_mode')
    def validate_gateway_mode(cls, v):
        if v is None:
            return v
        valid_modes = ["manual", "auto_first", "none"]
        if v not in valid_modes:
            raise ValueError(f"Invalid gateway mode. Must be one of: {valid_modes}")
        return v


class SubnetOut(SubnetBase):
    id: int
    allocation_mode: str
    gateway_mode: str
    subnet_mask: int | None = None
    host_count: int | None = None

    class Config:
        from_attributes = True
