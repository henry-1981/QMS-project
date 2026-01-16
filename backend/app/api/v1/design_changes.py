from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.base import get_db
from app.db.models import DesignChange, User
from app.models.schemas import (
    DesignChangeCreate,
    DesignChangeResponse,
    DesignChangeUpdate,
    WorkflowTransition
)
from app.utils.auth import get_current_active_user

router = APIRouter()


@router.post("/", response_model=DesignChangeResponse)
def create_design_change(
    change: DesignChangeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    change_count = db.query(DesignChange).filter(
        DesignChange.project_id == change.project_id
    ).count()
    change_number = f"DCR-{change.project_id:04d}-{change_count + 1:03d}"
    
    db_change = DesignChange(
        change_number=change_number,
        project_id=change.project_id,
        title=change.title,
        description=change.description,
        change_type=change.change_type,
        justification=change.justification,
        figma_link=change.figma_link,
        gdocs_link=change.gdocs_link,
        created_by=current_user.id,
        workflow_status="draft"
    )
    db.add(db_change)
    db.commit()
    db.refresh(db_change)
    return db_change


@router.get("/{change_id}", response_model=DesignChangeResponse)
def get_design_change(
    change_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    change = db.query(DesignChange).filter(DesignChange.id == change_id).first()
    if not change:
        raise HTTPException(status_code=404, detail="Design change not found")
    return change


@router.get("/", response_model=List[DesignChangeResponse])
def list_design_changes(
    skip: int = 0,
    limit: int = 100,
    project_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(DesignChange)
    if project_id:
        query = query.filter(DesignChange.project_id == project_id)
    changes = query.offset(skip).limit(limit).all()
    return changes


@router.put("/{change_id}", response_model=DesignChangeResponse)
def update_design_change(
    change_id: int,
    change_update: DesignChangeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_change = db.query(DesignChange).filter(DesignChange.id == change_id).first()
    if not db_change:
        raise HTTPException(status_code=404, detail="Design change not found")
    
    update_data = change_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_change, field, value)
    
    db.commit()
    db.refresh(db_change)
    return db_change


@router.post("/{change_id}/transition", response_model=DesignChangeResponse)
def transition_workflow(
    change_id: int,
    transition: WorkflowTransition,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_change = db.query(DesignChange).filter(DesignChange.id == change_id).first()
    if not db_change:
        raise HTTPException(status_code=404, detail="Design change not found")
    
    workflow_transitions = {
        "submit_for_ra": "ra_review",
        "ra_approve": "implementation",
        "submit_for_qa": "qa_review",
        "qa_approve": "quality_head_approval",
        "approve": "approved",
        "reject": "rejected"
    }
    
    new_status = workflow_transitions.get(transition.action)
    if not new_status:
        raise HTTPException(status_code=400, detail="Invalid transition action")
    
    from app.db.models import WorkflowHistory
    history = WorkflowHistory(
        change_id=change_id,
        from_status=db_change.workflow_status,
        to_status=new_status,
        action=transition.action,
        comments=transition.comments,
        performed_by=current_user.id
    )
    db.add(history)
    
    db_change.workflow_status = new_status  # type: ignore
    db.commit()
    db.refresh(db_change)
    return db_change
