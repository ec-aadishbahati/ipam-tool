from pydantic import BaseModel


class PurposeBase(BaseModel):
    name: str
    description: str | None = None
    category: str | None = None
    category_id: int | None = None


class PurposeCreate(PurposeBase):
    pass


class PurposeUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category: str | None = None
    category_id: int | None = None


class PurposeOut(PurposeBase):
    id: int

    class Config:
        from_attributes = True
