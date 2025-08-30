from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime


class BackupMetadata(BaseModel):
    created_at: datetime
    version: str
    total_records: int
    created_by_user_id: int
    backup_id: str


class BackupData(BaseModel):
    users: List[Dict[str, Any]]
    categories: List[Dict[str, Any]]
    purposes: List[Dict[str, Any]]
    racks: List[Dict[str, Any]]
    supernets: List[Dict[str, Any]]
    vlans: List[Dict[str, Any]]
    subnets: List[Dict[str, Any]]
    devices: List[Dict[str, Any]]
    ip_assignments: List[Dict[str, Any]]


class BackupFile(BaseModel):
    metadata: BackupMetadata
    data: BackupData


class BackupListItem(BaseModel):
    backup_id: str
    filename: str
    created_at: datetime
    size_bytes: int
    total_records: int
    created_by_user_id: int


class RestoreResult(BaseModel):
    success: bool
    message: str
    records_imported: Dict[str, int]
    errors: List[str] = []
