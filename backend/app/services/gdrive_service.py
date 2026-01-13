from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from typing import List, Dict, Optional
import io
import pandas as pd
from app.core.config import settings


class GoogleDriveService:
    def __init__(self):
        self.credentials = service_account.Credentials.from_service_account_file(
            settings.GOOGLE_DRIVE_CREDENTIALS_PATH,
            scopes=['https://www.googleapis.com/auth/drive.readonly']
        )
        self.service = build('drive', 'v3', credentials=self.credentials)
    
    def list_files(self, folder_id: Optional[str] = None, query: Optional[str] = None) -> List[Dict]:
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
        try:
            content = self.download_file(file_id)
            df = pd.read_excel(io.BytesIO(content))
            return df
        except Exception as e:
            print(f"Error reading Excel file: {e}")
            return pd.DataFrame()
    
    def get_file_metadata(self, file_id: str) -> Dict:
        try:
            file = self.service.files().get(
                fileId=file_id,
                fields='id, name, mimeType, modifiedTime, size, parents'
            ).execute()
            return file
        except Exception as e:
            print(f"Error getting file metadata: {e}")
            return {}


gdrive_service = GoogleDriveService()
