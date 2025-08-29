from pydantic import BaseModel


class RackBase(BaseModel):
    aisle: str
    rack_number: str
    position_count: int = 42
    power_type: str | None = None
    power_capacity: str | None = None
    cooling_type: str | None = None
    location: str | None = None
    notes: str | None = None


class RackCreate(RackBase):
    pass


class RackUpdate(BaseModel):
    aisle: str | None = None
    rack_number: str | None = None
    position_count: int | None = None
    power_type: str | None = None
    power_capacity: str | None = None
    cooling_type: str | None = None
    location: str | None = None
    notes: str | None = None


class RackOut(RackBase):
    id: int

    class Config:
        from_attributes = True
