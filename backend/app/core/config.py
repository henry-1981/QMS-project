from typing import List
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
    
    GOOGLE_API_KEY: str
    GOOGLE_DRIVE_CREDENTIALS_PATH: str
    
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
