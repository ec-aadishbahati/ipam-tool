from pydantic import BaseModel, validator
from app.core.validators import validate_ip_address_format


class IpAssignmentBase(BaseModel):
    subnet_id: int
    device_id: int | None = None
    ip_address: str
    role: str | None = None

    @validator('ip_address')
    def validate_ip_address(cls, v):
        return validate_ip_address_format(v)


class IpAssignmentCreate(IpAssignmentBase):
    pass


class IpAssignmentUpdate(BaseModel):
    device_id: int | None = None
    ip_address: str | None = None
    role: str | None = None

    @validator('ip_address')
    def validate_ip_address(cls, v):
        if v is None:
            return v
        return validate_ip_address_format(v)


class IpAssignmentOut(IpAssignmentBase):
    id: int

    class Config:
        from_attributes = True
