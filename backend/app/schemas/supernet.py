from pydantic import BaseModel


class SupernetBase(BaseModel):
    cidr: str
    name: str | None = None
    site: str | None = None
    environment: str | None = None


class SupernetCreate(SupernetBase):
    pass


class SupernetUpdate(BaseModel):
    cidr: str | None = None
    name: str | None = None
    site: str | None = None
    environment: str | None = None


class SupernetOut(SupernetBase):
    id: int
    utilization_percentage: float | None = None

    class Config:
        from_attributes = True
