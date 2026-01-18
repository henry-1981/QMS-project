from typing import Dict, Any, List, Optional
import json
import logging
from app.agents.base_agent import BaseAgent, AgentState
from app.services.vector_db_service import vector_db_service

logger = logging.getLogger(__name__)


class VerificationValidationAgent(BaseAgent):
    def __init__(self):
        super().__init__("verification_validation")
    
    def create_verification_plan_prompt(self, change_data: Dict[str, Any], sop_guidance: str) -> str:
        return f"""당신은 의료기기 검증/밸리데이션 전문가입니다.

[설계 변경 내용]
제목: {change_data.get('title', '')}
설명: {change_data.get('description', '')}
변경 유형: {change_data.get('change_type', '')}

[SOP 검증 지침]
{sop_guidance}

검증 계획을 작성하세요. JSON 형식:
{{
  "verification_plan": {{
    "test_objectives": ["목적 1", "목적 2"],
    "test_scope": "테스트 범위",
    "test_approach": "테스트 접근 방법",
    "success_criteria": ["성공 기준 1", "성공 기준 2"]
  }},
  "test_cases": [
    {{
      "test_id": "TC-001",
      "test_name": "테스트 이름",
      "test_type": "unit/integration/system",
      "priority": "high/medium/low",
      "preconditions": ["사전조건 1"],
      "test_steps": ["단계 1", "단계 2"],
      "expected_results": ["예상 결과 1"],
      "acceptance_criteria": "합격 기준"
    }}
  ],
  "validation_requirements": {{
    "user_acceptance_needed": true/false,
    "clinical_evaluation_needed": true/false,
    "performance_evaluation_needed": true/false,
    "usability_validation_needed": true/false
  }},
  "required_documentation": [
    "문서 1",
    "문서 2"
  ],
  "estimated_effort": {{
    "preparation_hours": 0,
    "execution_hours": 0,
    "review_hours": 0,
    "total_hours": 0
  }},
  "recommendations": ["권장사항 1", "권장사항 2"]
}}

반드시 JSON 형식으로만 응답하세요."""
    
    def create_checklist_prompt(self, change_type: str, iec_62304_class: str, sop_guidance: str) -> str:
        return f"""당신은 의료기기 검증/밸리데이션 전문가입니다.

[변경 유형]
{change_type}

[IEC 62304 소프트웨어 등급]
{iec_62304_class}

[SOP 체크리스트 참조]
{sop_guidance}

검증 체크리스트를 생성하세요. JSON 형식:
{{
  "checklist_items": [
    {{
      "item_id": "CHK-001",
      "category": "설계 검증/코드 리뷰/테스트",
      "item_description": "체크 항목 설명",
      "verification_method": "검증 방법",
      "acceptance_criteria": "합격 기준",
      "reference_document": "참조 문서",
      "mandatory": true/false,
      "applicable_for_class": ["A", "B", "C"]
    }}
  ],
  "summary": {{
    "total_items": 0,
    "mandatory_items": 0,
    "optional_items": 0
  }},
  "iec_62304_requirements": [
    "IEC 62304 요구사항 1",
    "IEC 62304 요구사항 2"
  ]
}}

반드시 JSON 형식으로만 응답하세요."""
    
    async def generate_verification_plan(self, change_data: Dict[str, Any]) -> Dict[str, Any]:
        sop_results = vector_db_service.search(
            collection_name="qms_knowledge_base",
            query=f"설계 검증 테스트 계획 {change_data.get('change_type', '')}",
            n_results=5
        )
        
        sop_guidance = "\n".join(sop_results.get('documents', [[]])[0]) if sop_results.get('documents') else ""
        
        prompt = self.create_verification_plan_prompt(change_data, sop_guidance)
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
    
    async def generate_checklist(
        self,
        change_type: str,
        iec_62304_class: str = "B"
    ) -> Dict[str, Any]:
        sop_results = vector_db_service.search(
            collection_name="qms_knowledge_base",
            query=f"검증 체크리스트 IEC 62304 Class {iec_62304_class}",
            n_results=5
        )
        
        sop_guidance = "\n".join(sop_results.get('documents', [[]])[0]) if sop_results.get('documents') else ""
        
        prompt = self.create_checklist_prompt(change_type, iec_62304_class, sop_guidance)
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
    
    async def review_verification_results(
        self,
        test_results: Dict[str, Any],
        acceptance_criteria: Dict[str, Any]
    ) -> Dict[str, Any]:
        prompt = f"""당신은 의료기기 검증/밸리데이션 전문가입니다.

[테스트 결과]
{test_results}

[합격 기준]
{acceptance_criteria}

테스트 결과를 검토하세요. JSON 형식:
{{
  "verification_status": "passed/failed/partial",
  "passed_tests": 0,
  "failed_tests": 0,
  "blocked_tests": 0,
  "critical_failures": ["실패 항목 1"],
  "non_critical_failures": ["실패 항목 2"],
  "coverage_assessment": {{
    "requirements_coverage": 0.0,
    "test_coverage": 0.0,
    "gaps": ["갭 1", "갭 2"]
  }},
  "recommendation": "approve/conditional_approve/reject",
  "conditions": ["조건 1", "조건 2"],
  "next_steps": ["다음 단계 1", "다음 단계 2"]
}}

반드시 JSON 형식으로만 응답하세요."""
        
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
        state['messages'].append(f"[{self.agent_type}] 설계 변경 {change_id}에 대한 검증 계획 수립 시작")
        
        try:
            design_change = self._get_design_change(change_id)
            
            if not design_change:
                logger.error(f"설계 변경 ID {change_id}를 찾을 수 없음")
                state['analysis_results']['verification_validation'] = {
                    'status': 'error',
                    'error': f'설계 변경 ID {change_id}를 찾을 수 없습니다'
                }
                return state
            
            project = self._get_project_for_change(change_id)
            
            change_data = {
                'title': design_change.title,
                'description': design_change.description,
                'change_type': design_change.change_type
            }
            
            verification_result = await self.generate_verification_plan(change_data)
            
            iec_class = project.iec_62304_class if project else "B"
            checklist_result = await self.generate_checklist(
                design_change.change_type or "일반",
                iec_class
            )
            
            state['messages'].append(f"[{self.agent_type}] 검증 계획 수립 완료")
            state['analysis_results']['verification_validation'] = {
                'status': 'completed',
                'verification_plan': verification_result,
                'checklist': checklist_result
            }
            
        except Exception as e:
            logger.exception(f"검증/밸리데이션 분석 중 오류 발생: {e}")
            state['messages'].append(f"[{self.agent_type}] 분석 중 오류 발생: {str(e)}")
            state['analysis_results']['verification_validation'] = {
                'status': 'error',
                'error': str(e)
            }
        
        return state


verification_agent = VerificationValidationAgent()
