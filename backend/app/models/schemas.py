from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    role: str


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


class GoogleLoginResponse(BaseModel):
    login_url: str
    message: str


class DesignProjectBase(BaseModel):
    project_code: str
    project_name: str
    description: Optional[str] = None
    product_type: Optional[str] = None
    iec_62304_class: Optional[str] = None


class DesignProjectCreate(DesignProjectBase):
    pass


class DesignProjectResponse(DesignProjectBase):
    id: int
    status: str
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DesignChangeBase(BaseModel):
    title: str
    description: str
    change_type: Optional[str] = None
    justification: Optional[str] = None
    figma_link: Optional[str] = None
    gdocs_link: Optional[str] = None


class DesignChangeCreate(DesignChangeBase):
    project_id: int


class DesignChangeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    change_type: Optional[str] = None
    justification: Optional[str] = None
    figma_link: Optional[str] = None
    gdocs_link: Optional[str] = None
    workflow_status: Optional[str] = None


class DesignChangeResponse(DesignChangeBase):
    id: int
    change_number: str
    project_id: int
    workflow_status: str
    current_assignee: Optional[int] = None
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class WorkflowTransition(BaseModel):
    action: str
    comments: Optional[str] = None


class AgentAnalysisRequest(BaseModel):
    change_id: int
    agent_type: str
    analysis_type: str
    model_name: Optional[str] = "gemini-1.5-pro"


class GeminiModelResponse(BaseModel):
    name: str
    display_name: str
    description: str


class AgentAnalysisResponse(BaseModel):
    id: int
    change_id: int
    agent_type: str
    analysis_type: str
    findings: Dict[str, Any]
    recommendations: Optional[List[str]] = None
    affected_items: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class RiskItemBase(BaseModel):
    risk_number: str
    project_id: int
    hazard: str
    hazardous_situation: Optional[str] = None
    harm: Optional[str] = None
    severity: Optional[int] = Field(None, ge=1, le=5)
    probability: Optional[int] = Field(None, ge=1, le=5)
    risk_level: Optional[str] = None
    control_measures: Optional[str] = None
    residual_risk_level: Optional[str] = None


class RiskItemCreate(RiskItemBase):
    pass


class RiskItemResponse(RiskItemBase):
    id: int
    excel_file_id: Optional[str] = None
    excel_row_number: Optional[int] = None
    last_synced_at: Optional[datetime] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DocumentBase(BaseModel):
    document_type: str
    document_code: str
    document_name: str
    version: str
    gdrive_file_id: Optional[str] = None
    gdrive_file_path: Optional[str] = None


class DocumentCreate(DocumentBase):
    project_id: Optional[int] = None


class DocumentResponse(DocumentBase):
    id: int
    project_id: Optional[int] = None
    status: str
    created_by: int
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ElectronicSignatureCreate(BaseModel):
    entity_type: str
    entity_id: int
    signature_meaning: str


class ElectronicSignatureResponse(BaseModel):
    id: int
    entity_type: str
    entity_id: int
    signer_id: int
    signature_meaning: str
    signed_at: datetime
    
    class Config:
        from_attributes = True
