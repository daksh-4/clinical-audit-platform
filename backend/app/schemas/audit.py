"""
Pydantic schemas for Audit entities.
"""
from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.models.audit import AuditStatus, DataProtectionLevel, QuestionType


class AuditBase(BaseModel):
    """Base audit schema."""
    title: str
    description: Optional[str] = None
    clinical_domain: str
    population: str
    start_date: datetime
    end_date: Optional[datetime] = None
    governance_body: Optional[str] = None


class AuditCreate(AuditBase):
    """Schema for creating a new audit."""
    data_protection_level: DataProtectionLevel = DataProtectionLevel.NO_PII
    is_public: bool = False
    require_consent: bool = False
    retention_days: int = 3650
    
    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, v: Optional[datetime], info) -> Optional[datetime]:
        if v and info.data.get("start_date") and v < info.data["start_date"]:
            raise ValueError("End date must be after start date")
        return v


class AuditUpdate(BaseModel):
    """Schema for updating an audit."""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[AuditStatus] = None
    end_date: Optional[datetime] = None
    is_public: Optional[bool] = None


class AuditResponse(AuditBase):
    """Schema for audit in API responses."""
    id: str
    status: AuditStatus
    data_protection_level: DataProtectionLevel
    owner_id: str
    is_public: bool
    total_episodes: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class QuestionCreate(BaseModel):
    """Schema for creating a question."""
    question_code: str
    question_text: str
    question_type: QuestionType
    help_text: Optional[str] = None
    clinical_guidance: Optional[str] = None
    required: bool = True
    options: Optional[Dict[str, Any]] = None
    validation: Optional[Dict[str, Any]] = None
    conditional_logic: Optional[Dict[str, Any]] = None
    variable_name: str
    variable_type: str
    variable_description: Optional[str] = None
    validated_instrument: Optional[str] = None


class QuestionResponse(QuestionCreate):
    """Schema for question in API responses."""
    id: str
    order_index: int
    has_guidance_warning: bool
    warning_message: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class QuestionnaireCreate(BaseModel):
    """Schema for creating a questionnaire."""
    title: str
    description: Optional[str] = None
    questions: List[QuestionCreate]


class QuestionnaireResponse(BaseModel):
    """Schema for questionnaire in API responses."""
    id: str
    audit_id: str
    version: int
    title: str
    description: Optional[str] = None
    is_published: bool
    published_at: Optional[datetime] = None
    methodological_quality_score: Optional[float] = None
    analysability_score: Optional[float] = None
    questions: List[QuestionResponse]
    created_at: datetime
    
    class Config:
        from_attributes = True


class EpisodeCreate(BaseModel):
    """Schema for creating an audit episode."""
    episode_code: Optional[str] = None
    responses: Dict[str, Any]
    consent_obtained: Optional[bool] = None
    consent_date: Optional[datetime] = None


class EpisodeResponse(BaseModel):
    """Schema for episode in API responses."""
    id: str
    audit_id: str
    questionnaire_version: int
    site_id: str
    submitted_by_id: str
    submitted_at: datetime
    episode_code: Optional[str] = None
    pseudonym: Optional[str] = None
    is_validated: bool
    responses: Dict[str, Any]
    derived_metrics: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class DPIACreate(BaseModel):
    """Schema for creating a DPIA."""
    assessment_data: Dict[str, Any]


class DPIAResponse(BaseModel):
    """Schema for DPIA in API responses."""
    id: str
    audit_id: str
    status: str
    risk_score: Optional[int] = None
    risk_level: Optional[str] = None
    dpo_reviewed: bool
    approved_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ExportRequest(BaseModel):
    """Schema for requesting a data export."""
    export_type: str = "csv"  # csv, json, excel
    justification: str
    include_pii: bool = False


class ExportResponse(BaseModel):
    """Schema for export in API responses."""
    id: str
    audit_id: str
    export_type: str
    records_count: int
    contains_pii: bool
    download_url: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
