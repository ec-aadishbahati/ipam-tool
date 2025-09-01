from pydantic import BaseModel
from typing import Generic, TypeVar, List

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    limit: int
    total_pages: int
    
    @classmethod
    def create(cls, items: List[T], total: int, page: int, limit: int):
        total_pages = (total + limit - 1) // limit  # Ceiling division
        return cls(items=items, total=total, page=page, limit=limit, total_pages=total_pages)
