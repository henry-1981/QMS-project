import google.generativeai as genai
from typing import List, Dict, Any, Optional
from app.core.config import settings
import google.auth
from google.oauth2.credentials import Credentials
from langchain_google_genai import ChatGoogleGenerativeAI

class GeminiService:
    def __init__(self):
        self.api_key = settings.GOOGLE_API_KEY
        genai.configure(api_key=self.api_key)

    def list_available_models(self) -> List[Dict[str, Any]]:
        """사용 가능한 Gemini 모델 목록을 반환합니다."""
        models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                models.append({
                    "name": m.name,
                    "display_name": m.display_name,
                    "description": m.description,
                })
        return models

    def get_chat_model(self, model_name: str, credentials: Optional[Credentials] = None) -> ChatGoogleGenerativeAI:
        """선택된 모델과 인증 정보로 Chat 모델을 생성합니다."""
        if credentials:
            return ChatGoogleGenerativeAI(
                model=model_name,
                credentials=credentials,
                temperature=0.1
            )
        else:
            return ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=self.api_key,
                temperature=0.1
            )

gemini_service = GeminiService()
