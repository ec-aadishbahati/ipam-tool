from pydantic import BaseModel


class VlanBase(BaseModel):
    site: str
    environment: str
    vlan_id: int
    name: str
    purpose_id: int | None = None


class VlanCreate(VlanBase):
    pass


class VlanUpdate(BaseModel):
    site: str | None = None
    environment: str | None = None
    vlan_id: int | None = None
    name: str | None = None
    purpose_id: int | None = None


class VlanOut(VlanBase):
    id: int

    class Config:
        from_attributes = True
