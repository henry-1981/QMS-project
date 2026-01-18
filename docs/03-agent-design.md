# 에이전트 상세 설계

## 1. 개요

QMS Agent System은 6개의 전문화된 AI 에이전트로 구성됩니다. 각 에이전트는 의료기기 설계 관리 프로세스의 특정 역할을 담당하며, LangGraph 기반 Orchestrator가 협업을 조율합니다.

## 2. 에이전트 계층 구조

```
                     ┌─────────────────────────┐
                     │   Agent Orchestrator    │
                     │    (LangGraph 기반)      │
                     └───────────┬─────────────┘
                                 │
           ┌─────────────────────┼─────────────────────┐
           │                     │                     │
           ▼                     ▼                     ▼
    ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
    │   Phase 1   │       │   Phase 2   │       │   Phase 3   │
    │  영향 분석   │ ────▶ │  위험 평가   │ ────▶ │ 규제/검증    │
    └─────────────┘       └─────────────┘       └─────────────┘
           │                     │                     │
     ┌─────┴─────┐         ┌─────┴─────┐         ┌─────┴─────┐
     ▼           ▼         ▼           ▼         ▼           ▼
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│ Design  │ │   PM    │ │   QA    │ │  Risk   │ │   RA    │ │Verificat│
│Engineer │ │  Agent  │ │  Agent  │ │ Manager │ │  Agent  │ │  Agent  │
└─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘
```

## 3. 공통 에이전트 인터페이스 (BaseAgent)

모든 에이전트는 `BaseAgent` 클래스를 상속합니다.

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

class AgentState(TypedDict):
    change_id: int
    messages: List[str]
    analysis_results: Dict[str, Any]
    current_agent: str
    workflow_status: str
    errors: List[str]

class BaseAgent(ABC):
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.gemini_service = GeminiService()
    
    @abstractmethod
    async def execute(self, state: AgentState) -> AgentState:
        pass
    
    def _get_db_session(self) -> Session:
        pass
    
    def _get_design_change(self, change_id: int) -> Optional[DesignChange]:
        pass
    
    def _get_project_for_change(self, change_id: int) -> Optional[DesignProject]:
        pass
    
    def _get_risks_for_project(self, project_id: int) -> List[RiskItem]:
        pass
```

## 4. 에이전트 상세 설계

### 4.1 Design Engineer Agent (설계 엔지니어 에이전트)

**역할**: 설계 변경의 기술적 영향을 분석합니다.

**주요 기능**:
- 변경 범위 및 영향도 분석
- 관련 컴포넌트/모듈 식별
- 기술적 리스크 평가
- 구현 복잡도 추정

**입력**:
```python
{
    "change_id": int,
    "change_description": str,
    "change_type": str,
    "figma_link": Optional[str],
    "gdocs_link": Optional[str]
}
```

**출력**:
```python
{
    "impact_score": float,  # 0.0 ~ 1.0
    "affected_components": List[str],
    "complexity_estimate": str,  # "low", "medium", "high"
    "technical_risks": List[Dict],
    "recommendations": List[str]
}
```

**프롬프트 구조**:
```
당신은 의료기기 설계 엔지니어입니다.
다음 설계 변경 요청을 분석하고 기술적 영향을 평가해주세요.

## 설계 변경 정보
- 제목: {title}
- 설명: {description}
- 변경 유형: {change_type}
- 변경 사유: {justification}

## 분석 요청 사항
1. 영향받는 시스템 컴포넌트 식별
2. 기술적 리스크 평가
3. 구현 복잡도 추정
4. 권고 사항 제시
```

### 4.2 PM Agent (프로젝트 매니저 에이전트)

**역할**: 일정 및 리소스 영향을 평가합니다.

**주요 기능**:
- 일정 영향 분석
- 리소스 요구사항 평가
- 마일스톤 조정 제안
- 병목 지점 식별

**출력**:
```python
{
    "schedule_impact": {
        "delay_estimate_days": int,
        "affected_milestones": List[str],
        "critical_path_impact": bool
    },
    "resource_requirements": {
        "additional_hours": int,
        "required_skills": List[str],
        "team_availability": str
    },
    "recommendations": List[str]
}
```

### 4.3 QA Agent (품질 보증 에이전트)

**역할**: 품질 요구사항 및 테스트 영향을 분석합니다.

**주요 기능**:
- 품질 요구사항 검토
- 테스트 케이스 영향 분석
- 이전 테스트 결과 검토
- 검증 전략 제안

**출력**:
```python
{
    "quality_impact": {
        "affected_requirements": List[str],
        "test_coverage_gap": float,
        "regression_risk": str
    },
    "test_recommendations": {
        "new_tests_needed": List[str],
        "tests_to_update": List[str],
        "automation_suggestions": List[str]
    },
    "findings": List[Dict]
}
```

### 4.4 RA Agent (규제 담당 에이전트)

**역할**: ISO 13485 및 MFDS 규제 적합성을 검토합니다.

**주요 기능**:
- ISO 13485 조항별 적합성 검토
- MFDS 요구사항 충족 여부 확인
- 규제 문서 영향 분석
- 인허가 절차 영향 평가

**출력**:
```python
{
    "regulatory_impact": {
        "iso_13485_clauses": List[Dict],  # 영향받는 조항
        "mfds_requirements": List[Dict],   # MFDS 요구사항
        "documentation_updates": List[str],
        "certification_impact": str
    },
    "compliance_status": {
        "overall": str,  # "compliant", "review_needed", "non_compliant"
        "findings": List[Dict],
        "required_actions": List[str]
    }
}
```

**ISO 13485 검토 항목**:
- 4.2 문서 요구사항
- 7.3 설계 및 개발
- 7.3.7 설계 및 개발 변경 관리
- 7.5 생산 및 서비스 제공
- 8.5 개선

### 4.5 Risk Manager Agent (리스크 관리자 에이전트)

**역할**: ISO 14971 기반 위험 분석 및 평가를 수행합니다.

**주요 기능**:
- 기존 위험 항목 재평가
- 신규 위험 식별
- 위험 통제 조치 검토
- 잔존 위험 평가

**출력**:
```python
{
    "existing_risks": {
        "reassessed": List[Dict],
        "status_changes": List[Dict],
        "new_controls_needed": List[str]
    },
    "new_risks": {
        "identified": List[Dict],  # hazard, severity, probability
        "proposed_controls": List[str]
    },
    "risk_matrix_updates": {
        "items_to_update": List[Dict],
        "overall_risk_level": str
    }
}
```

**위험 평가 기준**:
| 심각도 | 설명 |
|--------|------|
| 1 | 무시 가능 (Negligible) |
| 2 | 경미 (Minor) |
| 3 | 심각 (Serious) |
| 4 | 치명적 (Critical) |
| 5 | 재앙적 (Catastrophic) |

| 발생 가능성 | 설명 |
|-------------|------|
| 1 | 거의 불가능 (Improbable) |
| 2 | 낮음 (Remote) |
| 3 | 가끔 (Occasional) |
| 4 | 자주 (Probable) |
| 5 | 빈번 (Frequent) |

### 4.6 Verification Agent (검증 담당 에이전트)

**역할**: IEC 62304 기반 검증 계획을 생성합니다.

**주요 기능**:
- 검증 계획 생성
- IEC 62304 등급별 체크리스트 생성
- 검증 활동 정의
- 추적성 요구사항 확인

**출력**:
```python
{
    "verification_plan": {
        "activities": List[Dict],
        "test_levels": List[str],  # unit, integration, system
        "acceptance_criteria": List[str]
    },
    "iec_62304_checklist": {
        "class": str,  # "A", "B", "C"
        "required_items": List[Dict],
        "documentation_required": List[str]
    },
    "traceability_requirements": {
        "items": List[Dict],
        "gaps": List[str]
    }
}
```

**IEC 62304 등급별 요구사항**:

| 등급 | 설명 | 필수 활동 |
|------|------|----------|
| Class A | 부상/건강 손상 없음 | 기본 개발 프로세스 |
| Class B | 심각하지 않은 부상 | 문서화 + 리뷰 |
| Class C | 사망/심각한 부상 가능 | 전체 V&V 활동 |

## 5. Orchestrator 설계

### 5.1 LangGraph 상태 머신

```python
from langgraph.graph import StateGraph

def create_agent_workflow() -> StateGraph:
    workflow = StateGraph(AgentState)
    
    # 노드 추가
    workflow.add_node("design_engineer", design_engineer_node)
    workflow.add_node("pm", pm_node)
    workflow.add_node("risk_manager", risk_manager_node)
    workflow.add_node("qa", qa_node)
    workflow.add_node("ra", ra_node)
    workflow.add_node("verification", verification_node)
    
    # 엣지 정의 (순차 실행)
    workflow.set_entry_point("design_engineer")
    workflow.add_edge("design_engineer", "pm")
    workflow.add_edge("pm", "risk_manager")
    workflow.add_edge("risk_manager", "qa")
    workflow.add_edge("qa", "ra")
    workflow.add_edge("ra", "verification")
    workflow.add_edge("verification", END)
    
    return workflow.compile()
```

### 5.2 실행 흐름

```
1. 설계 변경 제출
       │
       ▼
2. Design Engineer Agent
   - 기술적 영향 분석
   - 영향받는 컴포넌트 식별
       │
       ▼
3. PM Agent
   - 일정/리소스 영향 평가
   - 마일스톤 조정 제안
       │
       ▼
4. Risk Manager Agent
   - 기존 위험 재평가
   - 신규 위험 식별
       │
       ▼
5. QA Agent
   - 품질 요구사항 검토
   - 테스트 영향 분석
       │
       ▼
6. RA Agent
   - 규제 적합성 검토
   - 문서 영향 분석
       │
       ▼
7. Verification Agent
   - 검증 계획 생성
   - 체크리스트 생성
       │
       ▼
8. 분석 결과 저장 (agent_analysis 테이블)
```

## 6. Gemini AI 연동

### 6.1 GeminiService

```python
class GeminiService:
    def __init__(self):
        self.model_name = "gemini-1.5-pro"
        genai.configure(api_key=settings.GOOGLE_API_KEY)
    
    async def analyze(
        self,
        prompt: str,
        context: Optional[str] = None,
        output_schema: Optional[Dict] = None
    ) -> Dict[str, Any]:
        model = genai.GenerativeModel(self.model_name)
        
        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        
        response = await model.generate_content_async(
            full_prompt,
            generation_config={
                "temperature": 0.2,
                "top_p": 0.8,
                "max_output_tokens": 4096
            }
        )
        
        return self._parse_response(response.text, output_schema)
```

### 6.2 프롬프트 템플릿

각 에이전트는 역할에 맞는 프롬프트 템플릿을 사용합니다:

```python
DESIGN_ENGINEER_PROMPT = """
당신은 ISO 13485 인증 의료기기 개발팀의 설계 엔지니어입니다.

## 배경
- 제품 유형: {product_type}
- IEC 62304 등급: {iec_62304_class}
- 프로젝트: {project_name}

## 설계 변경 정보
{change_details}

## 분석 요청
다음 항목에 대해 분석해주세요:
1. 영향받는 시스템 컴포넌트
2. 기술적 리스크
3. 구현 복잡도 (low/medium/high)
4. 권고 사항

JSON 형식으로 응답해주세요.
"""
```

## 7. RAG 지식베이스 (예정)

### 7.1 문서 구성

| 문서 유형 | 설명 |
|----------|------|
| 설계 및 개발 관리 절차서 | 메인 SOP |
| 소프트웨어 개발 지침서 | IEC 62304 가이드 |
| 사용적합성 지침서 | IEC 62366 가이드 |

### 7.2 ChromaDB 연동 (예정)

```python
class RAGKnowledgeBase:
    def __init__(self):
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection("qms_docs")
    
    def add_document(self, doc_id: str, content: str, metadata: Dict):
        self.collection.add(
            documents=[content],
            metadatas=[metadata],
            ids=[doc_id]
        )
    
    def query(self, query: str, n_results: int = 5) -> List[Dict]:
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results
```

## 8. 에러 처리

```python
class AgentError(Exception):
    def __init__(self, agent_name: str, message: str, details: Dict = None):
        self.agent_name = agent_name
        self.message = message
        self.details = details or {}
        super().__init__(f"[{agent_name}] {message}")

class AgentTimeoutError(AgentError):
    pass

class AgentValidationError(AgentError):
    pass
```

## 9. 로깅 및 모니터링

```python
import logging

logger = logging.getLogger("qms.agents")

async def execute_with_logging(agent: BaseAgent, state: AgentState) -> AgentState:
    logger.info(f"[{agent.name}] 분석 시작 - change_id: {state['change_id']}")
    
    try:
        result = await agent.execute(state)
        logger.info(f"[{agent.name}] 분석 완료")
        return result
    except Exception as e:
        logger.error(f"[{agent.name}] 분석 실패: {str(e)}")
        state["errors"].append(f"{agent.name}: {str(e)}")
        return state
```
