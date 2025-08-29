from pydantic import BaseModel


class PurposeBase(BaseModel):
    name: str
    description: str | None = None
    category: str | None = None


class PurposeCreate(PurposeBase):
    pass


class PurposeUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category: str | None = None


class PurposeOut(PurposeBase):
    id: int

    class Config:
        from_attributes = True
