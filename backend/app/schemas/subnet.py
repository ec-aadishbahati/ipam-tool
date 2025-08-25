from pydantic import BaseModel


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


class SubnetOut(SubnetBase):
    id: int

    class Config:
        from_attributes = True
