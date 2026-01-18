from typing import List, Dict, Any, Optional, Union
from enum import Enum
from app.services.gdrive_service import gdrive_service, GoogleDriveService
from app.services.local_storage_service import local_storage_service, LocalStorageService


class StorageType(str, Enum):
    LOCAL = "local"
    GDRIVE = "gdrive"


class DocumentManager:
    """통합 문서 관리자 - 로컬 및 Google Drive 추상화"""
    
    def __init__(
        self, 
        local_service: LocalStorageService = local_storage_service,
        gdrive_service: GoogleDriveService = gdrive_service
    ):
        self.local = local_service
        self.gdrive = gdrive_service
    
    def list_documents(
        self, 
        storage: StorageType = StorageType.LOCAL,
        category: str = "",
        folder_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """문서 목록 조회"""
        if storage == StorageType.LOCAL:
            return self.local.list_files(category=category)
        else:
            return self.gdrive.list_files(folder_id=folder_id)
    
    def read_document(
        self,
        path_or_id: str,
        storage: StorageType = StorageType.LOCAL
    ) -> str:
        """문서 내용 읽기"""
        if storage == StorageType.LOCAL:
            return self.local.read_file(path_or_id)
        else:
            return self.gdrive.get_file_content(path_or_id)
    
    def save_document(
        self,
        content: str,
        name: str,
        storage: StorageType = StorageType.LOCAL,
        category: str = "documents",
        folder_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """문서 저장"""
        if storage == StorageType.LOCAL:
            file_path = f"{category}/{name}"
            saved_path = self.local.write_file(file_path, content)
            return {"path": saved_path, "storage": "local"}
        else:
            result = self.gdrive.upload_content(content, name, folder_id=folder_id)
            if result:
                result["storage"] = "gdrive"
            return result
    
    def get_sop(self, sop_name: str, storage: StorageType = StorageType.LOCAL) -> str:
        """SOP 문서 가져오기"""
        if storage == StorageType.LOCAL:
            return self.local.read_file(f"sop/{sop_name}")
        else:
            # Google Drive에서 SOP 폴더 내 검색
            files = self.gdrive.list_files(query=f"name contains '{sop_name}'")
            if files:
                return self.gdrive.get_file_content(files[0]['id'])
            return ""
    
    def save_analysis_record(
        self,
        record_type: str,
        data: Dict[str, Any],
        storage: StorageType = StorageType.LOCAL,
        folder_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """분석 결과 기록 저장"""
        if storage == StorageType.LOCAL:
            saved_path = self.local.save_record(record_type, data)
            return {"path": saved_path, "storage": "local"}
        else:
            import json
            from datetime import datetime
            filename = f"{record_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            content = json.dumps(data, ensure_ascii=False, indent=2)
            result = self.gdrive.upload_content(content, filename, folder_id=folder_id, mime_type='application/json')
            if result:
                result["storage"] = "gdrive"
            return result
    
    def sync_to_gdrive(self, local_path: str, gdrive_folder_id: str) -> Optional[Dict]:
        """로컬 파일을 Google Drive로 동기화"""
        content = self.local.read_file(local_path)
        filename = local_path.split("/")[-1]
        return self.gdrive.upload_content(content, filename, folder_id=gdrive_folder_id)
    
    def sync_to_local(self, gdrive_file_id: str, local_category: str = "documents") -> str:
        """Google Drive 파일을 로컬로 동기화"""
        metadata = self.gdrive.get_file_metadata(gdrive_file_id)
        content = self.gdrive.get_file_content(gdrive_file_id)
        filename = metadata.get('name', 'downloaded_file.txt')
        return self.local.write_file(f"{local_category}/{filename}", content)


document_manager = DocumentManager()
