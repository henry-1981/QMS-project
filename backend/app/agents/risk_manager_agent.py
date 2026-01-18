from typing import Dict, Any, List, Optional
import json
import logging
from app.agents.base_agent import BaseAgent, AgentState
from app.services.vector_db_service import vector_db_service
from app.services.gdrive_service import gdrive_service

logger = logging.getLogger(__name__)


class RiskManagerAgent(BaseAgent):
    def __init__(self):
        super().__init__("risk_manager")
    
    def create_prompt_reassess(self, risk_data: str, change_description: str, iso_guidance: str) -> str:
        return f"""당신은 의료기기 리스크 관리 전문가입니다.

[설계 변경 내용]
{change_description}

[영향받는 기존 위험]
{risk_data}

[ISO 14971 가이드]
{iso_guidance}

각 위험 항목에 대해 재평가하세요. JSON 형식:
{{
  "reassessed_risks": [
    {{
      "risk_number": "위험 번호",
      "current_severity": 1-5,
      "current_probability": 1-5,
      "new_severity": 1-5,
      "new_probability": 1-5,
      "risk_level_before": "low/medium/high/unacceptable",
      "risk_level_after": "low/medium/high/unacceptable",
      "change_rationale": "변경 이유",
      "additional_controls_needed": true/false,
      "recommended_controls": ["통제 수단 1", "통제 수단 2"]
    }}
  ],
  "summary": {{
    "total_risks_reassessed": 0,
    "risks_increased": 0,
    "risks_decreased": 0,
    "risks_unchanged": 0,
    "requires_immediate_action": true/false
  }},
  "recommendations": ["권장사항 1", "권장사항 2"]
}}

반드시 JSON 형식으로만 응답하세요."""
    
    def create_prompt_identify(self, change_description: str, usability_guidance: str) -> str:
        return f"""당신은 의료기기 리스크 관리 전문가입니다.

[설계 변경 내용]
{change_description}

[IEC 62366 사용적합성 가이드]
{usability_guidance}

신규 위험을 식별하세요. JSON 형식:
{{
  "new_risks": [
    {{
      "hazard": "위해요인",
      "hazardous_situation": "위해상황",
      "harm": "위해",
      "severity": 1-5,
      "probability": 1-5,
      "risk_level": "low/medium/high/unacceptable",
      "recommended_controls": ["통제 수단 1", "통제 수단 2"],
      "residual_risk_estimate": "잔여 위험 예상"
    }}
  ],
  "risk_categories": {{
    "safety_risks": 0,
    "usability_risks": 0,
    "performance_risks": 0,
    "other_risks": 0
  }},
  "priority_risks": ["우선순위 높은 위험 설명"],
  "recommendations": ["권장사항 1", "권장사항 2"]
}}

반드시 JSON 형식으로만 응답하세요."""
    
    async def reassess_existing_risks(
        self,
        existing_risks: List[Dict[str, Any]],
        change_description: str
    ) -> Dict[str, Any]:
        iso_results = vector_db_service.search(
            collection_name="qms_knowledge_base",
            query="ISO 14971 위험 재평가",
            n_results=3
        )
        
        iso_guidance = "\n".join(iso_results.get('documents', [[]])[0]) if iso_results.get('documents') else ""
        risk_data = str(existing_risks)
        
        prompt = self.create_prompt_reassess(risk_data, change_description, iso_guidance)
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
    
    async def identify_new_risks(self, change_description: str) -> Dict[str, Any]:
        usability_results = vector_db_service.search(
            collection_name="qms_knowledge_base",
            query="IEC 62366 사용 오류 위험",
            n_results=3
        )
        
        usability_guidance = "\n".join(usability_results.get('documents', [[]])[0]) if usability_results.get('documents') else ""
        
        prompt = self.create_prompt_identify(change_description, usability_guidance)
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
    
    async def update_risk_excel(self, risk_file_id: str, updates: List[Dict[str, Any]]) -> bool:
        try:
            import pandas as pd
            df = gdrive_service.read_excel_file(risk_file_id)
            
            for update in updates:
                risk_number = update.get('risk_number')
                mask = df['risk_number'] == risk_number
                if mask.any():
                    for key, value in update.items():
                        if key in df.columns:
                            df.loc[mask, key] = value
            
            return True
        except Exception as e:
            logger.error(f"위험 관리 엑셀 업데이트 실패: {e}")
            return False
    
    async def execute(self, state: AgentState) -> AgentState:
        change_id = state['change_id']
        state['messages'].append(f"[{self.agent_type}] 설계 변경 {change_id}에 대한 위험 관리 시작")
        
        try:
            design_change = self._get_design_change(change_id)
            
            if not design_change:
                logger.error(f"설계 변경 ID {change_id}를 찾을 수 없음")
                state['analysis_results']['risk_manager'] = {
                    'status': 'error',
                    'error': f'설계 변경 ID {change_id}를 찾을 수 없습니다'
                }
                return state
            
            project = self._get_project_for_change(change_id)
            existing_risks: List[Dict[str, Any]] = []
            
            if project:
                risk_items = self._get_risks_for_project(project.id)
                existing_risks = [
                    {
                        'risk_number': r.risk_number,
                        'hazard': r.hazard,
                        'hazardous_situation': r.hazardous_situation,
                        'harm': r.harm,
                        'severity': r.severity,
                        'probability': r.probability,
                        'risk_level': r.risk_level
                    }
                    for r in risk_items
                ]
            
            reassess_result = await self.reassess_existing_risks(
                existing_risks,
                design_change.description
            )
            
            new_risks_result = await self.identify_new_risks(design_change.description)
            
            state['messages'].append(f"[{self.agent_type}] 위험 관리 완료")
            state['analysis_results']['risk_manager'] = {
                'status': 'completed',
                'reassessed_risks': reassess_result,
                'new_risks': new_risks_result
            }
            
        except Exception as e:
            logger.exception(f"위험 관리자 분석 중 오류 발생: {e}")
            state['messages'].append(f"[{self.agent_type}] 분석 중 오류 발생: {str(e)}")
            state['analysis_results']['risk_manager'] = {
                'status': 'error',
                'error': str(e)
            }
        
        return state


risk_manager_agent = RiskManagerAgent()
