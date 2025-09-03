from pydantic import BaseModel
from typing import List

class BulkDeleteRequest(BaseModel):
    ids: List[int]

class BulkDeleteResponse(BaseModel):
    deleted_count: int
    errors: List[str] = []

class BulkExportRequest(BaseModel):
    ids: List[int]

class BulkUpdateRequest(BaseModel):
    ids: List[int]
    updates: dict

class BulkUpdateResponse(BaseModel):
    updated_count: int
    errors: List[str] = []
