from typing import TypedDict, Annotated, Sequence, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
import operator
from app.core.config import settings


class AgentState(TypedDict):
    messages: Annotated[Sequence[str], operator.add]
    change_id: int
    user_role: str
    current_step: str
    analysis_results: Dict[str, Any]
    next_agent: str


class BaseAgent:
    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.1
        )
    
    def create_prompt(self, task: str, context: Dict[str, Any]) -> str:
        raise NotImplementedError("Subclasses must implement create_prompt")
    
    async def execute(self, state: AgentState) -> AgentState:
        raise NotImplementedError("Subclasses must implement execute")
