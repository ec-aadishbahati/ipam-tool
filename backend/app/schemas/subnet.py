from pydantic import BaseModel, validator, model_validator
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

    @model_validator(mode='before')
    @classmethod
    def validate_subnet_fields(cls, values):
        if not isinstance(values, dict):
            return values
            
        
        allocation_mode = values.get('allocation_mode', 'manual')
        gateway_mode = values.get('gateway_mode', 'manual')
        cidr = values.get('cidr')
        gateway_ip = values.get('gateway_ip')
        
        if allocation_mode == 'manual':
            if not cidr or cidr == "":
                raise ValueError("CIDR is required for manual allocation mode")
            validate_cidr_format(cidr)
        elif allocation_mode in ['auto_mask', 'auto_hosts']:
            pass
        
        if gateway_mode == 'manual':
            if gateway_ip and gateway_ip != "":
                validate_ip_address_format(gateway_ip)
                if cidr and not validate_gateway_in_subnet(gateway_ip, cidr):
                    raise ValueError(f"Gateway IP {gateway_ip} is not usable within subnet {cidr}")
        elif gateway_mode in ['auto_first', 'none']:
            pass
        
        return values

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

    @model_validator(mode='before')
    @classmethod
    def validate_subnet_update_fields(cls, values):
        if not isinstance(values, dict):
            return values
            
        
        allocation_mode = values.get('allocation_mode', 'manual')
        gateway_mode = values.get('gateway_mode', 'manual')
        cidr = values.get('cidr')
        gateway_ip = values.get('gateway_ip')
        
        if cidr is not None and cidr != "":
            if allocation_mode == 'manual':
                validate_cidr_format(cidr)
            elif allocation_mode in ['auto_mask', 'auto_hosts']:
                pass
        
        if gateway_ip is not None and gateway_ip != "":
            if gateway_mode == 'manual':
                validate_ip_address_format(gateway_ip)
                if cidr and not validate_gateway_in_subnet(gateway_ip, cidr):
                    raise ValueError(f"Gateway IP {gateway_ip} is not usable within subnet {cidr}")
            elif gateway_mode in ['auto_first', 'none']:
                pass
        
        return values

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
    utilization_percentage: float | None = None
    available_ips: int | None = None
    first_ip: str | None = None
    last_ip: str | None = None

    class Config:
        from_attributes = True
