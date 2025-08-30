from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import json
import os
from pathlib import Path

from app.api.deps import get_current_user
from app.db.session import get_db
from app.services.backup import (
    create_backup, list_backups, restore_backup, 
    get_backup_file_path, delete_backup_file
)
from app.schemas.backup import BackupListItem, RestoreResult

router = APIRouter()


@router.post("/create")
async def create_system_backup(
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    """Create a complete system backup"""
    try:
        backup_id = await create_backup(db, user.id)
        return {
            "success": True,
            "message": "Backup created successfully",
            "backup_id": backup_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backup creation failed: {str(e)}")


@router.get("/list", response_model=List[BackupListItem])
async def list_system_backups(user = Depends(get_current_user)):
    """List all available backup files"""
    try:
        return await list_backups()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list backups: {str(e)}")


@router.get("/download/{backup_id}")
async def download_backup(
    backup_id: str,
    user = Depends(get_current_user)
):
    """Download a backup file"""
    filepath = get_backup_file_path(backup_id)
    if not filepath or not filepath.exists():
        raise HTTPException(status_code=404, detail="Backup file not found")
    
    return FileResponse(
        path=str(filepath),
        filename=filepath.name,
        media_type="application/json"
    )


@router.post("/restore", response_model=RestoreResult)
async def restore_system_backup(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    """Restore system from backup file"""
    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="File must be a JSON backup file")
    
    try:
        content = await file.read()
        backup_data = json.loads(content.decode('utf-8'))
        
        result = await restore_backup(db, backup_data)
        return result
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Restore failed: {str(e)}")


@router.delete("/{backup_id}")
async def delete_system_backup(
    backup_id: str,
    user = Depends(get_current_user)
):
    """Delete a backup file"""
    success = delete_backup_file(backup_id)
    if not success:
        raise HTTPException(status_code=404, detail="Backup file not found")
    
    return {"success": True, "message": "Backup deleted successfully"}
