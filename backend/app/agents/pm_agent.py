from typing import Dict, Any, Optional
import json
import logging
from app.agents.base_agent import BaseAgent, AgentState
from app.services.vector_db_service import vector_db_service

logger = logging.getLogger(__name__)


class ProjectManagerAgent(BaseAgent):
    def __init__(self):
        super().__init__("project_manager")
    
    def create_prompt(self, change_data: Dict[str, Any], project_context: str) -> str:
        return f"""당신은 의료기기 프로젝트 관리자(PM)입니다.

[설계 변경 내용]
제목: {change_data.get('title', '')}
설명: {change_data.get('description', '')}
변경 유형: {change_data.get('change_type', '')}

[프로젝트 정보]
{project_context}

다음을 JSON 형식으로 분석하세요:
{{
  "schedule_impact": {{
    "estimated_effort_hours": 0,
    "critical_path_impact": true/false,
    "suggested_timeline": "일정 제안",
    "milestones_affected": ["마일스톤 1", "마일스톤 2"]
  }},
  "resource_allocation": {{
    "required_roles": ["역할 1", "역할 2"],
    "estimated_fte": 0.0,
    "skill_requirements": ["스킬 1", "스킬 2"],
    "resource_conflicts": ["충돌 사항"]
  }},
  "dependencies": {{
    "blocking_items": ["차단 항목 1"],
    "dependent_items": ["종속 항목 1"],
    "external_dependencies": ["외부 종속성"]
  }},
  "risk_factors": {{
    "schedule_risks": ["일정 위험 1"],
    "resource_risks": ["리소스 위험 1"],
    "mitigation_strategies": ["완화 전략 1"]
  }},
  "recommendations": [
    "권장사항 1",
    "권장사항 2"
  ],
  "priority_assessment": "high" | "medium" | "low",
  "comments": "종합 의견"
}}

반드시 JSON 형식으로만 응답하세요."""
    
    async def assess_project_impact(self, change_data: Dict[str, Any]) -> Dict[str, Any]:
        project_info = f"프로젝트 코드: {change_data.get('project_code', 'N/A')}"
        
        sop_results = vector_db_service.search(
            collection_name="qms_knowledge_base",
            query="프로젝트 관리 일정 리소스",
            n_results=3
        )
        
        project_context = project_info + "\n\n[SOP 참조]\n"
        if sop_results.get('documents'):
            project_context += "\n".join(sop_results['documents'][0])
        
        prompt = self.create_prompt(change_data, project_context)
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
        state['messages'].append(f"[{self.agent_type}] 설계 변경 {change_id}에 대한 프로젝트 영향 평가 시작")
        
        try:
            design_change = self._get_design_change(change_id)
            
            if not design_change:
                logger.error(f"설계 변경 ID {change_id}를 찾을 수 없음")
                state['analysis_results']['project_manager'] = {
                    'status': 'error',
                    'error': f'설계 변경 ID {change_id}를 찾을 수 없습니다'
                }
                return state
            
            project = self._get_project_for_change(change_id)
            
            change_data = {
                'title': design_change.title,
                'description': design_change.description,
                'change_type': design_change.change_type,
                'project_code': project.project_code if project else 'N/A'
            }
            
            pm_result = await self.assess_project_impact(change_data)
            
            state['messages'].append(f"[{self.agent_type}] 프로젝트 영향 평가 완료")
            state['analysis_results']['project_manager'] = {
                'status': 'completed',
                'project_impact': pm_result
            }
            
        except Exception as e:
            logger.exception(f"프로젝트 매니저 분석 중 오류 발생: {e}")
            state['messages'].append(f"[{self.agent_type}] 분석 중 오류 발생: {str(e)}")
            state['analysis_results']['project_manager'] = {
                'status': 'error',
                'error': str(e)
            }
        
        return state


pm_agent = ProjectManagerAgent()
