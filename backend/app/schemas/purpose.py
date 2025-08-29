from pydantic import BaseModel
from app.schemas.category import CategoryOut


class PurposeBase(BaseModel):
    name: str
    description: str | None = None
    category_id: int | None = None


class PurposeCreate(PurposeBase):
    pass


class PurposeUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category_id: int | None = None


class PurposeOut(PurposeBase):
    id: int
    category: CategoryOut | None = None

    class Config:
        from_attributes = True
