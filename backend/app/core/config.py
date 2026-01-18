from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl


class Settings(BaseSettings):
    PROJECT_NAME: str = "QMS Agent System"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    DATABASE_URL: str
    
    GOOGLE_API_KEY: Optional[str] = None
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = "http://localhost:8000/api/v1/auth/google/callback"
    GOOGLE_DRIVE_CREDENTIALS_PATH: Optional[str] = None
    
    GOOGLE_OAUTH_SCOPES: List[str] = [
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/drive.readonly",
    ]
    
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    LOCAL_STORAGE_PATH: str = "./qms_storage"
    
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    FRONTEND_URL: str = "http://localhost:5173"
    
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
