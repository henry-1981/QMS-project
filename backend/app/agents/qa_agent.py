from typing import Dict, Any, Optional
import json
import logging
from app.agents.base_agent import BaseAgent, AgentState
from app.services.vector_db_service import vector_db_service

logger = logging.getLogger(__name__)


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
        
        try:
            content = response.content
            if isinstance(content, str):
                result = json.loads(content)
            else:
                result = {"error": "응답이 문자열 형식이 아님", "raw": str(content)}
        except json.JSONDecodeError as e:
            logger.warning(f"JSON 파싱 실패: {e}")
            result = {"error": "JSON 파싱 실패", "raw": str(response.content)}
        
        return result
    
    async def execute(self, state: AgentState) -> AgentState:
        change_id = state['change_id']
        state['messages'].append(f"[{self.agent_type}] 설계 변경 {change_id}에 대한 품질 검토 시작")
        
        try:
            design_change = self._get_design_change(change_id)
            
            if not design_change:
                logger.error(f"설계 변경 ID {change_id}를 찾을 수 없음")
                state['analysis_results']['quality_assurance'] = {
                    'status': 'error',
                    'error': f'설계 변경 ID {change_id}를 찾을 수 없습니다'
                }
                return state
            
            change_data = {
                'title': design_change.title,
                'description': design_change.description,
                'change_type': design_change.change_type
            }
            
            previous_results = state.get('analysis_results', {})
            test_results = previous_results.get('verification_validation', {}).get('verification_plan', {})
            
            if not test_results:
                test_results = {
                    'total_tests': 0,
                    'passed': 0,
                    'failed': 0,
                    'details': '검증 결과 대기 중'
                }
            
            qa_result = await self.review_test_results(change_data, test_results)
            
            state['messages'].append(f"[{self.agent_type}] 품질 검토 완료")
            state['analysis_results']['quality_assurance'] = {
                'status': 'completed',
                'quality_review': qa_result
            }
            
        except Exception as e:
            logger.exception(f"품질 보증 분석 중 오류 발생: {e}")
            state['messages'].append(f"[{self.agent_type}] 분석 중 오류 발생: {str(e)}")
            state['analysis_results']['quality_assurance'] = {
                'status': 'error',
                'error': str(e)
            }
        
        return state


qa_agent = QualityAssuranceAgent()
