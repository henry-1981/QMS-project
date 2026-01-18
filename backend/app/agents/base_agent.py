from typing import TypedDict, Annotated, Sequence, Dict, Any, Optional, List
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
import operator
from app.core.config import settings
from app.db.base import SessionLocal
from app.db.models import DesignChange, DesignProject, RiskItem

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    messages: Annotated[List[str], operator.add]
    change_id: int
    user_role: str
    current_step: str
    analysis_results: Dict[str, Any]
    next_agent: str


class BaseAgent:
    def __init__(self, agent_type: str, model_name: str = "gemini-1.5-pro"):
        self.agent_type = agent_type
        self.model_name = model_name
        self._init_llm()
    
    def _get_db_session(self):
        """DB 세션을 반환합니다."""
        return SessionLocal()
    
    def _get_design_change(self, change_id: int) -> Optional[DesignChange]:
        """설계 변경 정보를 DB에서 조회합니다."""
        db = self._get_db_session()
        try:
            change = db.query(DesignChange).filter(DesignChange.id == change_id).first()
            return change
        finally:
            db.close()
    
    def _get_project_for_change(self, change_id: int) -> Optional[DesignProject]:
        """설계 변경에 연결된 프로젝트 정보를 조회합니다."""
        db = self._get_db_session()
        try:
            change = db.query(DesignChange).filter(DesignChange.id == change_id).first()
            if change and change.project_id:
                return db.query(DesignProject).filter(DesignProject.id == change.project_id).first()
            return None
        finally:
            db.close()
    
    def _get_risks_for_project(self, project_id: int) -> List[RiskItem]:
        """프로젝트의 위험 항목들을 조회합니다."""
        db = self._get_db_session()
        try:
            risks = db.query(RiskItem).filter(RiskItem.project_id == project_id).all()
            return risks
        finally:
            db.close()
    
    def _init_llm(self, model_name: Optional[str] = None, credentials: Any = None):
        if model_name:
            self.model_name = model_name
        
        args = {
            "model": self.model_name,
            "temperature": 0.1
        }
        
        if credentials:
            args["credentials"] = credentials
        else:
            args["google_api_key"] = settings.GOOGLE_API_KEY
            
        self.llm = ChatGoogleGenerativeAI(**args)
    
    def create_prompt(self, task: str, context: Dict[str, Any]) -> str:
        raise NotImplementedError("Subclasses must implement create_prompt")
    
    async def execute(self, state: AgentState) -> AgentState:
        raise NotImplementedError("Subclasses must implement execute")
