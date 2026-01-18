from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from typing import List, Optional
from app.db.models import User
from app.utils.auth import get_current_active_user
from app.services.document_manager import document_manager, StorageType
from app.services.local_storage_service import local_storage_service
from app.services.gdrive_service import gdrive_service
from pydantic import BaseModel
from datetime import datetime


router = APIRouter()


class FileInfo(BaseModel):
    name: str
    path: Optional[str] = None
    size: Optional[int] = None
    modified_at: Optional[str] = None
    extension: Optional[str] = None
    category: Optional[str] = None
    storage: str


class DocumentContent(BaseModel):
    content: str
    name: str
    category: Optional[str] = "documents"
    storage: str = "local"
    folder_id: Optional[str] = None


class DocumentResponse(BaseModel):
    path: Optional[str] = None
    id: Optional[str] = None
    storage: str
    webViewLink: Optional[str] = None


@router.get("/files", response_model=List[FileInfo])
async def list_files(
    storage: str = Query("local", enum=["local", "gdrive"]),
    category: str = Query("", description="로컬 저장소 카테고리 (sop, documents, records 등)"),
    folder_id: Optional[str] = Query(None, description="Google Drive 폴더 ID"),
    current_user: User = Depends(get_current_active_user)
):
    """파일 목록 조회 (로컬 또는 Google Drive)"""
    storage_type = StorageType(storage)
    files = document_manager.list_documents(storage=storage_type, category=category, folder_id=folder_id)
    
    return [
        FileInfo(
            name=f.get("name", ""),
            path=f.get("path") or f.get("id"),
            size=f.get("size"),
            modified_at=f.get("modified_at") or f.get("modifiedTime"),
            extension=f.get("extension"),
            category=f.get("category"),
            storage=storage
        )
        for f in files
    ]


@router.get("/files/content")
async def get_file_content(
    path_or_id: str,
    storage: str = Query("local", enum=["local", "gdrive"]),
    current_user: User = Depends(get_current_active_user)
):
    """파일 내용 읽기"""
    storage_type = StorageType(storage)
    try:
        content = document_manager.read_document(path_or_id, storage=storage_type)
        return {"content": content, "path_or_id": path_or_id, "storage": storage}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/files", response_model=DocumentResponse)
async def save_document(
    doc: DocumentContent,
    current_user: User = Depends(get_current_active_user)
):
    """문서 저장 (로컬 또는 Google Drive)"""
    storage_type = StorageType(doc.storage)
    result = document_manager.save_document(
        content=doc.content,
        name=doc.name,
        storage=storage_type,
        category=doc.category or "documents",
        folder_id=doc.folder_id
    )
    
    if not result:
        raise HTTPException(status_code=500, detail="Failed to save document")
    
    return DocumentResponse(
        path=result.get("path"),
        id=result.get("id"),
        storage=result.get("storage", doc.storage),
        webViewLink=result.get("webViewLink")
    )


@router.get("/sop/{sop_name}")
async def get_sop(
    sop_name: str,
    storage: str = Query("local", enum=["local", "gdrive"]),
    current_user: User = Depends(get_current_active_user)
):
    """SOP 문서 가져오기"""
    storage_type = StorageType(storage)
    content = document_manager.get_sop(sop_name, storage=storage_type)
    
    if not content:
        raise HTTPException(status_code=404, detail="SOP not found")
    
    return {"sop_name": sop_name, "content": content, "storage": storage}


@router.get("/categories")
async def list_categories(
    current_user: User = Depends(get_current_active_user)
):
    """로컬 저장소 카테고리 목록"""
    return {
        "categories": [
            {"name": "sop", "description": "Standard Operating Procedures"},
            {"name": "documents", "description": "일반 문서"},
            {"name": "records", "description": "기록 (보고서, 분석 결과 등)"},
            {"name": "templates", "description": "문서 템플릿"},
            {"name": "regulatory", "description": "규제 관련 문서"},
            {"name": "risk", "description": "위험 관리 문서"},
        ]
    }


@router.post("/sync/to-gdrive")
async def sync_to_gdrive(
    local_path: str,
    gdrive_folder_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """로컬 파일을 Google Drive로 동기화"""
    result = document_manager.sync_to_gdrive(local_path, gdrive_folder_id)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to sync to Google Drive")
    return result


@router.post("/sync/to-local")
async def sync_to_local(
    gdrive_file_id: str,
    local_category: str = "documents",
    current_user: User = Depends(get_current_active_user)
):
    """Google Drive 파일을 로컬로 동기화"""
    try:
        saved_path = document_manager.sync_to_local(gdrive_file_id, local_category)
        return {"saved_path": saved_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
