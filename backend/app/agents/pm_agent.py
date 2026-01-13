from typing import Dict, Any
from app.agents.base_agent import BaseAgent, AgentState
from app.services.vector_db_service import vector_db_service


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
        
        import json
        try:
            result = json.loads(response.content)
        except:
            result = {"error": "Failed to parse response", "raw": response.content}
        
        return result
    
    async def execute(self, state: AgentState) -> AgentState:
        change_id = state['change_id']
        
        state['messages'].append(f"[{self.agent_type}] Assessing project impact for change {change_id}")
        
        state['analysis_results']['project_manager'] = {
            'status': 'completed',
            'message': 'Project impact assessment completed'
        }
        
        return state


pm_agent = ProjectManagerAgent()
