from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)
    full_name = Column(String(200), nullable=False)
    role = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    
    google_id = Column(String(255), unique=True, nullable=True, index=True)
    google_refresh_token = Column(Text, nullable=True)
    google_access_token = Column(Text, nullable=True)
    google_token_expiry = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DesignProject(Base):
    __tablename__ = "design_projects"
    
    id = Column(Integer, primary_key=True, index=True)
    project_code = Column(String(50), unique=True, nullable=False, index=True)
    project_name = Column(String(255), nullable=False)
    description = Column(Text)
    product_type = Column(String(100))
    iec_62304_class = Column(String(10))
    status = Column(String(50), default='draft')
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    design_changes = relationship("DesignChange", back_populates="project")


class DesignChange(Base):
    __tablename__ = "design_changes"
    
    id = Column(Integer, primary_key=True, index=True)
    change_number = Column(String(50), unique=True, nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("design_projects.id"))
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    change_type = Column(String(50))
    justification = Column(Text)
    figma_link = Column(Text)
    gdocs_link = Column(Text)
    workflow_status = Column(String(50), default='draft', index=True)
    current_assignee = Column(Integer, ForeignKey("users.id"))
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    project = relationship("DesignProject", back_populates="design_changes")
    workflow_history = relationship("WorkflowHistory", back_populates="design_change")


class WorkflowHistory(Base):
    __tablename__ = "workflow_history"
    
    id = Column(Integer, primary_key=True, index=True)
    change_id = Column(Integer, ForeignKey("design_changes.id"))
    from_status = Column(String(50))
    to_status = Column(String(50))
    action = Column(String(50))
    comments = Column(Text)
    performed_by = Column(Integer, ForeignKey("users.id"))
    performed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    design_change = relationship("DesignChange", back_populates="workflow_history")


class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    document_type = Column(String(50), nullable=False)
    document_code = Column(String(100), unique=True, nullable=False)
    document_name = Column(String(255), nullable=False)
    version = Column(String(20), nullable=False)
    gdrive_file_id = Column(String(255), unique=True)
    gdrive_file_path = Column(Text)
    project_id = Column(Integer, ForeignKey("design_projects.id"))
    status = Column(String(50), default='draft')
    created_by = Column(Integer, ForeignKey("users.id"))
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TraceabilityLink(Base):
    __tablename__ = "traceability_links"
    
    id = Column(Integer, primary_key=True, index=True)
    source_type = Column(String(50), nullable=False, index=True)
    source_id = Column(Integer, nullable=False, index=True)
    target_type = Column(String(50), nullable=False, index=True)
    target_id = Column(Integer, nullable=False, index=True)
    relationship_type = Column(String(50))
    is_auto_generated = Column(Boolean, default=False)
    confidence_score = Column(Float)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class RiskItem(Base):
    __tablename__ = "risk_items"
    
    id = Column(Integer, primary_key=True, index=True)
    risk_number = Column(String(50), unique=True, nullable=False)
    project_id = Column(Integer, ForeignKey("design_projects.id"))
    hazard = Column(Text, nullable=False)
    hazardous_situation = Column(Text)
    harm = Column(Text)
    severity = Column(Integer)
    probability = Column(Integer)
    risk_level = Column(String(20))
    control_measures = Column(Text)
    residual_risk_level = Column(String(20))
    excel_file_id = Column(String(255))
    excel_row_number = Column(Integer)
    last_synced_at = Column(DateTime(timezone=True))
    status = Column(String(50), default='open')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ChangeRiskLink(Base):
    __tablename__ = "change_risk_links"
    
    id = Column(Integer, primary_key=True, index=True)
    change_id = Column(Integer, ForeignKey("design_changes.id"))
    risk_id = Column(Integer, ForeignKey("risk_items.id"))
    link_type = Column(String(50))
    analysis_summary = Column(Text)
    requires_reassessment = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AgentTask(Base):
    __tablename__ = "agent_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    task_type = Column(String(50), nullable=False)
    agent_type = Column(String(50), nullable=False)
    related_entity_type = Column(String(50))
    related_entity_id = Column(Integer)
    status = Column(String(50), default='pending', index=True)
    input_data = Column(JSON)
    output_data = Column(JSON)
    assigned_to = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))


class AgentAnalysis(Base):
    __tablename__ = "agent_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    change_id = Column(Integer, ForeignKey("design_changes.id"))
    agent_type = Column(String(50), nullable=False)
    analysis_type = Column(String(50))
    findings = Column(JSON)
    recommendations = Column(JSON)
    affected_items = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ElectronicSignature(Base):
    __tablename__ = "electronic_signatures"
    
    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=False)
    signer_id = Column(Integer, ForeignKey("users.id"))
    signature_meaning = Column(String(100))
    ip_address = Column(String(50))
    user_agent = Column(Text)
    signed_at = Column(DateTime(timezone=True), server_default=func.now())
