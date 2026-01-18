from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.db.models import DesignChange, User, AgentAnalysis
from app.models.schemas import AgentAnalysisRequest, AgentAnalysisResponse, GeminiModelResponse
from app.utils.auth import get_current_active_user
from app.agents.design_engineer_agent import design_engineer_agent
from app.agents.ra_agent import ra_agent
from app.agents.qa_agent import qa_agent
from app.services.gemini_service import gemini_service

router = APIRouter()


@router.get("/models", response_model=List[GeminiModelResponse])
async def list_models(
    current_user: User = Depends(get_current_active_user)
):
    """사용 가능한 Gemini 모델 목록을 가져옵니다."""
    return gemini_service.list_available_models()


@router.post("/analyze/impact", response_model=AgentAnalysisResponse)
async def analyze_impact(
    request: AgentAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    change = db.query(DesignChange).filter(DesignChange.id == request.change_id).first()
    if not change:
        raise HTTPException(status_code=404, detail="Design change not found")
    
    change_data = {
        "id": change.id,
        "title": change.title,
        "description": change.description,
        "change_type": change.change_type
    }
    
    # 모델 동적 설정
    if request.model_name:
        design_engineer_agent._init_llm(model_name=request.model_name)
    
    result = await design_engineer_agent.analyze_impact(change_data)
    
    analysis = AgentAnalysis(
        change_id=request.change_id,
        agent_type="design_engineer",
        analysis_type="impact",
        findings=result
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    
    return analysis


@router.post("/analyze/risk", response_model=AgentAnalysisResponse)
async def analyze_risk(
    request: AgentAnalysisRequest,
    risk_file_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    change = db.query(DesignChange).filter(DesignChange.id == request.change_id).first()
    if not change:
        raise HTTPException(status_code=404, detail="Design change not found")
    
    change_data = {
        "id": change.id,
        "title": change.title,
        "description": change.description,
        "change_type": change.change_type
    }
    
    # 모델 동적 설정
    if request.model_name:
        design_engineer_agent._init_llm(model_name=request.model_name)
        
    result = await design_engineer_agent.analyze_risks(change_data, risk_file_id)
    
    analysis = AgentAnalysis(
        change_id=request.change_id,
        agent_type="design_engineer",
        analysis_type="risk",
        findings=result
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    
    return analysis


@router.post("/analyze/regulatory", response_model=AgentAnalysisResponse)
async def analyze_regulatory(
    request: AgentAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    change = db.query(DesignChange).filter(DesignChange.id == request.change_id).first()
    if not change:
        raise HTTPException(status_code=404, detail="Design change not found")
    
    change_data = {
        "id": change.id,
        "title": change.title,
        "description": change.description,
        "product_type": change.project.product_type if change.project else None
    }
    
    result = await ra_agent.review_compliance(change_data)
    
    analysis = AgentAnalysis(
        change_id=request.change_id,
        agent_type="regulatory_affairs",
        analysis_type="regulation",
        findings=result
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    
    return analysis


@router.post("/analyze/qa", response_model=AgentAnalysisResponse)
async def analyze_qa(
    request: AgentAnalysisRequest,
    test_results: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    change = db.query(DesignChange).filter(DesignChange.id == request.change_id).first()
    if not change:
        raise HTTPException(status_code=404, detail="Design change not found")
    
    change_data = {
        "id": change.id,
        "description": change.description,
        "change_type": change.change_type
    }
    
    result = await qa_agent.review_test_results(change_data, test_results)
    
    analysis = AgentAnalysis(
        change_id=request.change_id,
        agent_type="quality_assurance",
        analysis_type="test",
        findings=result
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    
    return analysis
