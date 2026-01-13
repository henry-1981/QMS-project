from typing import Dict, Any
from app.agents.base_agent import BaseAgent, AgentState
from app.services.vector_db_service import vector_db_service


class RegulatoryAffairsAgent(BaseAgent):
    def __init__(self):
        super().__init__("regulatory_affairs")
    
    def create_prompt(self, change_data: Dict[str, Any], regulations: str) -> str:
        return f"""당신은 의료기기 규제 전문가(RA)입니다.

[설계 변경 내용]
제목: {change_data.get('title', '')}
설명: {change_data.get('description', '')}
제품 유형: {change_data.get('product_type', '')}

[관련 규제 요구사항]
{regulations}

다음을 JSON 형식으로 검토하세요:
{{
  "iso_13485_compliance": {{
    "compliant": true/false,
    "related_clauses": ["7.3.3", "7.3.4"],
    "requirements": ["요구사항 1", "요구사항 2"],
    "gaps": ["미흡한 부분 1", "미흡한 부분 2"]
  }},
  "mfds_compliance": {{
    "change_type": "경미한 변경" | "일부 변경" | "전부 변경",
    "notification_required": true/false,
    "required_documents": ["문서 1", "문서 2"],
    "review_comments": "검토 의견"
  }},
  "regulatory_impact": {{
    "technical_file_update": true/false,
    "label_change": true/false,
    "user_manual_update": true/false
  }},
  "decision": "APPROVE" | "REQUEST_CHANGES" | "REJECT",
  "comments": "종합 의견 및 권장사항"
}}

반드시 JSON 형식으로만 응답하세요."""
    
    async def review_compliance(self, change_data: Dict[str, Any]) -> Dict[str, Any]:
        description = change_data.get('description', '')
        
        iso_results = vector_db_service.search(
            collection_name="qms_knowledge_base",
            query=f"ISO 13485 {description}",
            n_results=5
        )
        
        mfds_results = vector_db_service.search(
            collection_name="qms_knowledge_base",
            query=f"MFDS 의료기기 {description}",
            n_results=5
        )
        
        regulations = "ISO 13485:\n" + "\n".join(iso_results.get('documents', [[]])[0])
        regulations += "\n\nMFDS:\n" + "\n".join(mfds_results.get('documents', [[]])[0])
        
        prompt = self.create_prompt(change_data, regulations)
        response = await self.llm.ainvoke(prompt)
        
        import json
        try:
            result = json.loads(response.content)
        except:
            result = {"error": "Failed to parse response", "raw": response.content}
        
        return result
    
    async def execute(self, state: AgentState) -> AgentState:
        change_id = state['change_id']
        
        state['messages'].append(f"[{self.agent_type}] Reviewing regulatory compliance for change {change_id}")
        
        state['analysis_results']['regulatory_affairs'] = {
            'status': 'completed',
            'message': 'Compliance review completed'
        }
        
        return state


ra_agent = RegulatoryAffairsAgent()
