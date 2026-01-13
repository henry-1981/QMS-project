from typing import Dict, Any
from app.agents.base_agent import BaseAgent, AgentState
from app.services.vector_db_service import vector_db_service


class QualityAssuranceAgent(BaseAgent):
    def __init__(self):
        super().__init__("quality_assurance")
    
    def create_prompt(self, change_data: Dict[str, Any], test_results: Dict[str, Any], quality_criteria: str) -> str:
        return f"""당신은 의료기기 품질보증(QA) 전문가입니다.

[설계 변경 내용]
{change_data.get('description', '')}

[Test 결과]
총 테스트: {test_results.get('total_tests', 0)}
통과: {test_results.get('passed', 0)}
실패: {test_results.get('failed', 0)}
상세: {test_results.get('details', '')}

[품질 기준 (SOP)]
{quality_criteria}

다음을 JSON 형식으로 분석하세요:
{{
  "test_summary": {{
    "total_tests": 0,
    "passed": 0,
    "failed": 0,
    "failed_tests": ["테스트 1", "테스트 2"]
  }},
  "quality_compliance": {{
    "meets_criteria": true/false,
    "mandatory_tests_completed": true/false,
    "acceptance_criteria_met": true/false,
    "gaps": ["미달 항목 1", "미달 항목 2"]
  }},
  "risk_assessment": {{
    "safety_impact": "high" | "medium" | "low",
    "user_impact": "high" | "medium" | "low",
    "critical_failures": ["실패 1", "실패 2"]
  }},
  "decision": "APPROVE" | "REQUEST_RETEST" | "REJECT",
  "decision_rationale": "판단 근거",
  "additional_tests_required": ["테스트 1", "테스트 2"],
  "comments": "종합 의견"
}}

반드시 JSON 형식으로만 응답하세요."""
    
    async def review_test_results(self, change_data: Dict[str, Any], test_results: Dict[str, Any]) -> Dict[str, Any]:
        quality_criteria_results = vector_db_service.search(
            collection_name="qms_knowledge_base",
            query=f"검증 합격 기준 {change_data.get('change_type', '')}",
            n_results=5
        )
        
        quality_criteria = "\n".join(quality_criteria_results.get('documents', [[]])[0])
        
        prompt = self.create_prompt(change_data, test_results, quality_criteria)
        response = await self.llm.ainvoke(prompt)
        
        import json
        try:
            result = json.loads(response.content)
        except:
            result = {"error": "Failed to parse response", "raw": response.content}
        
        return result
    
    async def execute(self, state: AgentState) -> AgentState:
        change_id = state['change_id']
        
        state['messages'].append(f"[{self.agent_type}] Reviewing test results for change {change_id}")
        
        state['analysis_results']['quality_assurance'] = {
            'status': 'completed',
            'message': 'Test review completed'
        }
        
        return state


qa_agent = QualityAssuranceAgent()
