from pydantic import BaseModel


class DeviceBase(BaseModel):
    name: str
    role: str | None = None
    hostname: str | None = None
    location: str | None = None
    vendor: str | None = None
    serial_number: str | None = None
    vlan_id: int | None = None
    rack_id: int | None = None
    rack_position: int | None = None


class DeviceCreate(DeviceBase):
    pass


class DeviceUpdate(BaseModel):
    name: str | None = None
    role: str | None = None
    hostname: str | None = None
    location: str | None = None
    vendor: str | None = None
    serial_number: str | None = None
    vlan_id: int | None = None
    rack_id: int | None = None
    rack_position: int | None = None


class DeviceOut(DeviceBase):
    id: int

    class Config:
        from_attributes = True
