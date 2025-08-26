from pydantic import BaseModel, validator
from app.core.validators import validate_cidr_format, validate_ip_address_format, validate_gateway_in_subnet


class SubnetBase(BaseModel):
    cidr: str
    name: str | None = None
    purpose_id: int | None = None
    assigned_to: str | None = None
    gateway_ip: str | None = None
    vlan_id: int | None = None
    site: str | None = None
    environment: str | None = None
    supernet_id: int | None = None

    @validator('cidr')
    def validate_cidr(cls, v):
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


class SubnetOut(SubnetBase):
    id: int

    class Config:
        from_attributes = True
