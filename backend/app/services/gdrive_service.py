from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload, MediaIoBaseUpload
from typing import List, Dict, Optional, Any, Union
import io
import pandas as pd
from app.core.config import settings


class GoogleDriveService:
    """Google Drive 파일 관리 서비스 (읽기/쓰기)"""
    
    SCOPES = [
        'https://www.googleapis.com/auth/drive.file',      # 생성한 파일에 대한 접근
        'https://www.googleapis.com/auth/drive.readonly',  # 모든 파일 읽기
    ]
    
    def __init__(self, credentials: Optional[Credentials] = None):
        self.service = None
        self._init_service(credentials)
    
    def _init_service(self, credentials: Optional[Credentials] = None):
        """서비스 초기화 - OAuth 또는 서비스 계정 사용"""
        try:
            if credentials:
                # OAuth 사용자 인증
                self.service = build('drive', 'v3', credentials=credentials)
            elif settings.GOOGLE_DRIVE_CREDENTIALS_PATH:
                # 서비스 계정 인증
                sa_credentials = service_account.Credentials.from_service_account_file(
                    settings.GOOGLE_DRIVE_CREDENTIALS_PATH,
                    scopes=self.SCOPES
                )
                self.service = build('drive', 'v3', credentials=sa_credentials)
        except Exception as e:
            print(f"Warning: Failed to initialize Google Drive service: {e}")
            self.service = None
    
    def reinitialize(self, credentials: Credentials):
        """사용자 OAuth 인증으로 서비스 재초기화"""
        self._init_service(credentials)
    
    def list_files(self, folder_id: Optional[str] = None, query: Optional[str] = None) -> List[Dict]:
        """파일 목록 조회"""
        if not self.service:
            return []
        try:
            if folder_id:
                query = f"'{folder_id}' in parents"
            
            results = self.service.files().list(
                q=query,
                fields="files(id, name, mimeType, modifiedTime, size)",
                pageSize=100
            ).execute()
            
            return results.get('files', [])
        except Exception as e:
            print(f"Error listing files: {e}")
            return []
    
    def download_file(self, file_id: str) -> bytes:
        """파일 다운로드"""
        if not self.service:
            return b""
        try:
            request = self.service.files().get_media(fileId=file_id)
            file_buffer = io.BytesIO()
            downloader = MediaIoBaseDownload(file_buffer, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            file_buffer.seek(0)
            return file_buffer.read()
        except Exception as e:
            print(f"Error downloading file: {e}")
            return b""
    
    def get_file_content(self, file_id: str) -> str:
        """Google Docs 등 텍스트 내용 가져오기"""
        if not self.service:
            return ""
        try:
            request = self.service.files().export_media(
                fileId=file_id,
                mimeType='text/plain'
            )
            file_buffer = io.BytesIO()
            downloader = MediaIoBaseDownload(file_buffer, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            file_buffer.seek(0)
            return file_buffer.read().decode('utf-8')
        except Exception as e:
            print(f"Error getting file content: {e}")
            return ""
    
    def read_excel_file(self, file_id: str) -> pd.DataFrame:
        """엑셀 파일 읽기"""
        try:
            content = self.download_file(file_id)
            df = pd.read_excel(io.BytesIO(content))
            return df
        except Exception as e:
            print(f"Error reading Excel file: {e}")
            return pd.DataFrame()
    
    def get_file_metadata(self, file_id: str) -> Dict:
        """파일 메타데이터 조회"""
        if not self.service:
            return {}
        try:
            file = self.service.files().get(
                fileId=file_id,
                fields='id, name, mimeType, modifiedTime, size, parents'
            ).execute()
            return file
        except Exception as e:
            print(f"Error getting file metadata: {e}")
            return {}
    
    def upload_file(
        self, 
        file_path: str, 
        name: str,
        folder_id: Optional[str] = None,
        mime_type: Optional[str] = None
    ) -> Optional[Dict]:
        """파일 업로드"""
        if not self.service:
            return None
        try:
            file_metadata: Dict[str, Any] = {'name': name}
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, mimeType, webViewLink'
            ).execute()
            return file
        except Exception as e:
            print(f"Error uploading file: {e}")
            return None
    
    def upload_content(
        self,
        content: Union[str, bytes],
        name: str,
        folder_id: Optional[str] = None,
        mime_type: str = 'text/plain'
    ) -> Optional[Dict]:
        """메모리 콘텐츠 업로드"""
        if not self.service:
            return None
        try:
            file_metadata: Dict[str, Any] = {'name': name}
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            if isinstance(content, str):
                content = content.encode('utf-8')
            
            media = MediaIoBaseUpload(io.BytesIO(content), mimetype=mime_type, resumable=True)
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, mimeType, webViewLink'
            ).execute()
            return file
        except Exception as e:
            print(f"Error uploading content: {e}")
            return None
    
    def create_folder(self, name: str, parent_id: Optional[str] = None) -> Optional[Dict]:
        """폴더 생성"""
        if not self.service:
            return None
        try:
            file_metadata: Dict[str, Any] = {
                'name': name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            if parent_id:
                file_metadata['parents'] = [parent_id]
            
            folder = self.service.files().create(
                body=file_metadata,
                fields='id, name, webViewLink'
            ).execute()
            return folder
        except Exception as e:
            print(f"Error creating folder: {e}")
            return None
    
    def update_file(self, file_id: str, content: Union[str, bytes], mime_type: str = 'text/plain') -> Optional[Dict]:
        """파일 내용 업데이트"""
        if not self.service:
            return None
        try:
            if isinstance(content, str):
                content = content.encode('utf-8')
            
            media = MediaIoBaseUpload(io.BytesIO(content), mimetype=mime_type, resumable=True)
            file = self.service.files().update(
                fileId=file_id,
                media_body=media,
                fields='id, name, modifiedTime'
            ).execute()
            return file
        except Exception as e:
            print(f"Error updating file: {e}")
            return None
    
    def delete_file(self, file_id: str) -> bool:
        """파일 삭제"""
        if not self.service:
            return False
        try:
            self.service.files().delete(fileId=file_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False


gdrive_service = GoogleDriveService()

