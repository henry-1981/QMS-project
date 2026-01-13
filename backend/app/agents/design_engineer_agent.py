from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent, AgentState
from app.services.vector_db_service import vector_db_service
from app.services.gdrive_service import gdrive_service


class DesignEngineerAgent(BaseAgent):
    def __init__(self):
        super().__init__("design_engineer")
    
    def create_prompt(self, task: str, context: Dict[str, Any]) -> str:
        if task == "impact_analysis":
            return f"""당신은 의료기기 설계 엔지니어 Assistant입니다.
다음 설계 변경 내용을 분석하고, 영향받는 문서 및 항목을 식별하세요.

[설계 변경 내용]
제목: {context.get('title', '')}
설명: {context.get('description', '')}

[관련 문서들]
{context.get('related_docs', '')}

다음을 JSON 형식으로 분석하세요:
1. 영향받는 문서 목록 (문서명, 버전, 영향 이유)
2. 영향받는 요구사항 (ID, 설명)
3. 영향받는 테스트 케이스
4. 수정이 필요한 항목들

반드시 JSON 형식으로만 응답하세요."""
        
        elif task == "risk_analysis":
            return f"""당신은 의료기기 리스크 관리 전문가입니다.

[설계 변경 내용]
{context.get('description', '')}

[기존 위험 관리 데이터]
{context.get('risk_data', '')}

다음을 JSON 형식으로 분석하세요:
1. existing_risks: 영향받는 기존 위험 항목들
   - risk_number: 위험 번호
   - risk_description: 위험 설명
   - impact_reason: 영향 이유
   - requires_reassessment: 재평가 필요 여부 (true/false)
   - risk_level_change: 위험 수준 변화 예상 (increase/decrease/maintain)

2. new_risks: 신규 위험 항목들
   - hazard: 위해요인
   - hazardous_situation: 위해상황
   - harm: 위해
   - severity: 심각도 (1-5)
   - probability: 발생 가능성 (1-5)
   - recommended_controls: 권장 통제 수단

반드시 JSON 형식으로만 응답하세요."""
        
        return ""
    
    async def analyze_impact(self, change_data: Dict[str, Any]) -> Dict[str, Any]:
        description = change_data.get('description', '')
        
        search_results = vector_db_service.search(
            collection_name="qms_knowledge_base",
            query=description,
            n_results=10
        )
        
        related_docs = "\n".join([
            f"- {doc}" for doc in search_results.get('documents', [[]])[0]
        ])
        
        context = {
            'title': change_data.get('title', ''),
            'description': description,
            'related_docs': related_docs
        }
        
        prompt = self.create_prompt("impact_analysis", context)
        response = await self.llm.ainvoke(prompt)
        
        import json
        try:
            result = json.loads(response.content)
        except:
            result = {"error": "Failed to parse response", "raw": response.content}
        
        return result
    
    async def analyze_risks(self, change_data: Dict[str, Any], risk_file_id: str) -> Dict[str, Any]:
        risk_df = gdrive_service.read_excel_file(risk_file_id)
        risk_data = risk_df.to_string() if not risk_df.empty else "No existing risk data"
        
        context = {
            'description': change_data.get('description', ''),
            'risk_data': risk_data
        }
        
        prompt = self.create_prompt("risk_analysis", context)
        response = await self.llm.ainvoke(prompt)
        
        import json
        try:
            result = json.loads(response.content)
        except:
            result = {"error": "Failed to parse response", "raw": response.content}
        
        return result
    
    async def execute(self, state: AgentState) -> AgentState:
        change_id = state['change_id']
        
        state['messages'].append(f"[{self.agent_type}] Starting analysis for change {change_id}")
        
        state['analysis_results']['design_engineer'] = {
            'status': 'completed',
            'message': 'Analysis completed'
        }
        
        return state


design_engineer_agent = DesignEngineerAgent()
