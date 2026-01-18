import os
import json
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
import pandas as pd
from app.core.config import settings


class LocalStorageService:
    """로컬 파일 시스템에서 QMS 문서를 관리하는 서비스"""
    
    def __init__(self, base_path: Optional[str] = None):
        self.base_path = Path(base_path or settings.LOCAL_STORAGE_PATH)
        self._ensure_directories()
    
    def _ensure_directories(self):
        """필수 디렉토리 구조 생성"""
        directories = [
            "sop",           # Standard Operating Procedures
            "documents",     # 일반 문서
            "records",       # 기록 (보고서, 분석 결과 등)
            "templates",     # 문서 템플릿
            "regulatory",    # 규제 관련 문서
            "risk",          # 위험 관리 문서
        ]
        for dir_name in directories:
            (self.base_path / dir_name).mkdir(parents=True, exist_ok=True)
    
    def list_files(
        self, 
        category: str = "", 
        extension: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """특정 카테고리의 파일 목록 조회"""
        target_path = self.base_path / category if category else self.base_path
        
        if not target_path.exists():
            return []
        
        files = []
        for item in target_path.rglob("*"):
            if item.is_file():
                if extension and not item.suffix.lower() == f".{extension.lower()}":
                    continue
                    
                stat = item.stat()
                files.append({
                    "name": item.name,
                    "path": str(item.relative_to(self.base_path)),
                    "absolute_path": str(item),
                    "size": stat.st_size,
                    "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "extension": item.suffix.lower(),
                    "category": category or "root"
                })
        
        return sorted(files, key=lambda x: x["modified_at"], reverse=True)
    
    def read_file(self, file_path: str) -> str:
        """텍스트 파일 읽기"""
        full_path = self.base_path / file_path
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        return full_path.read_text(encoding="utf-8")
    
    def read_json(self, file_path: str) -> Dict[str, Any]:
        """JSON 파일 읽기"""
        content = self.read_file(file_path)
        return json.loads(content)
    
    def read_excel(self, file_path: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """엑셀 파일 읽기"""
        full_path = self.base_path / file_path
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        return pd.read_excel(full_path, sheet_name=sheet_name)
    
    def write_file(self, file_path: str, content: str) -> str:
        """텍스트 파일 저장"""
        full_path = self.base_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")
        return str(full_path)
    
    def write_json(self, file_path: str, data: Dict[str, Any]) -> str:
        """JSON 파일 저장"""
        content = json.dumps(data, ensure_ascii=False, indent=2)
        return self.write_file(file_path, content)
    
    def write_excel(self, file_path: str, df: pd.DataFrame, sheet_name: str = "Sheet1") -> str:
        """엑셀 파일 저장"""
        full_path = self.base_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_excel(full_path, sheet_name=sheet_name, index=False)
        return str(full_path)
    
    def save_record(
        self, 
        record_type: str, 
        data: Dict[str, Any],
        filename: Optional[str] = None
    ) -> str:
        """분석 결과 등 기록 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if not filename:
            filename = f"{record_type}_{timestamp}.json"
        
        file_path = f"records/{record_type}/{filename}"
        return self.write_json(file_path, {
            "created_at": datetime.now().isoformat(),
            "record_type": record_type,
            "data": data
        })
    
    def delete_file(self, file_path: str) -> bool:
        """파일 삭제"""
        full_path = self.base_path / file_path
        if full_path.exists():
            full_path.unlink()
            return True
        return False
    
    def copy_file(self, source_path: str, dest_path: str) -> str:
        """파일 복사"""
        src = self.base_path / source_path
        dst = self.base_path / dest_path
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return str(dst)


local_storage_service = LocalStorageService()
