from pydantic import BaseModel


class IpAssignmentBase(BaseModel):
    subnet_id: int
    device_id: int | None = None
    ip_address: str
    role: str | None = None


class IpAssignmentCreate(IpAssignmentBase):
    pass


class IpAssignmentUpdate(BaseModel):
    device_id: int | None = None
    ip_address: str | None = None
    role: str | None = None


class IpAssignmentOut(IpAssignmentBase):
    id: int

    class Config:
        from_attributes = True
