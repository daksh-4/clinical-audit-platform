"""
Audit and questionnaire models.
"""
from sqlalchemy import String, Text, Boolean, Integer, Enum as SQLEnum, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
from datetime import datetime
import enum

from app.db.base import Base, TimestampMixin, UUIDMixin


class AuditStatus(str, enum.Enum):
    """Audit lifecycle status."""
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"
    ARCHIVED = "archived"


class DataProtectionLevel(str, enum.Enum):
    """Data protection classification."""
    NO_PII = "no_pii"
    PSEUDONYMISED = "pseudonymised"
    PII_REQUIRED = "pii_required"


class QuestionType(str, enum.Enum):
    """Question types for structured data capture."""
    CATEGORICAL_SINGLE = "categorical_single"
    CATEGORICAL_MULTIPLE = "categorical_multiple"
    ORDINAL = "ordinal"
    NUMERIC = "numeric"
    DATE = "date"
    TIME = "time"
    DATETIME = "datetime"
    TEXT_SHORT = "text_short"
    TEXT_LONG = "text_long"
    BOOLEAN = "boolean"


class Audit(Base, UUIDMixin, TimestampMixin):
    """
    Main audit entity.
    """
    __tablename__ = "audits"
    
    # Basic metadata
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    clinical_domain: Mapped[str] = mapped_column(String(100), nullable=False)
    population: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Timeframe
    start_date: Mapped[datetime] = mapped_column(nullable=False)
    end_date: Mapped[datetime] = mapped_column(nullable=True)
    
    # Status
    status: Mapped[AuditStatus] = mapped_column(
        SQLEnum(AuditStatus),
        default=AuditStatus.DRAFT,
        nullable=False,
    )
    
    # Governance
    governance_body: Mapped[str] = mapped_column(String(255), nullable=True)
    ethical_approval_ref: Mapped[str] = mapped_column(String(100), nullable=True)
    
    # Data protection
    data_protection_level: Mapped[DataProtectionLevel] = mapped_column(
        SQLEnum(DataProtectionLevel),
        default=DataProtectionLevel.NO_PII,
        nullable=False,
    )
    dpia_reference: Mapped[str] = mapped_column(String(100), nullable=True)
    retention_days: Mapped[int] = mapped_column(default=3650, nullable=False)
    
    # Ownership
    owner_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    
    # Settings
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    allow_duplicate_entries: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    require_consent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Metrics
    total_episodes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="owned_audits", foreign_keys=[owner_id])
    questionnaires: Mapped[List["Questionnaire"]] = relationship(
        "Questionnaire",
        back_populates="audit",
        cascade="all, delete-orphan",
    )
    episodes: Mapped[List["AuditEpisode"]] = relationship(
        "AuditEpisode",
        back_populates="audit",
        cascade="all, delete-orphan",
    )


class Questionnaire(Base, UUIDMixin, TimestampMixin):
    """
    Versioned questionnaire for an audit.
    """
    __tablename__ = "questionnaires"
    
    # Parent audit
    audit_id: Mapped[str] = mapped_column(String(36), ForeignKey("audits.id"), nullable=False)
    
    # Version control
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    published_at: Mapped[datetime] = mapped_column(nullable=True)
    
    # Metadata
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Quality scoring
    methodological_quality_score: Mapped[float] = mapped_column(nullable=True)
    analysability_score: Mapped[float] = mapped_column(nullable=True)
    
    # Relationships
    audit: Mapped[Audit] = relationship("Audit", back_populates="questionnaires")
    questions: Mapped[List["Question"]] = relationship(
        "Question",
        back_populates="questionnaire",
        cascade="all, delete-orphan",
        order_by="Question.order_index",
    )


class Question(Base, UUIDMixin, TimestampMixin):
    """
    Individual question within a questionnaire.
    """
    __tablename__ = "questions"
    
    # Parent questionnaire
    questionnaire_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("questionnaires.id"),
        nullable=False,
    )
    
    # Question details
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    question_code: Mapped[str] = mapped_column(String(50), nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[QuestionType] = mapped_column(
        SQLEnum(QuestionType),
        nullable=False,
    )
    
    # Help and guidance
    help_text: Mapped[str] = mapped_column(Text, nullable=True)
    clinical_guidance: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Required/optional
    required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Options for categorical/ordinal questions (JSON array)
    options: Mapped[dict] = mapped_column(JSON, nullable=True)
    
    # Validation rules (JSON object)
    validation: Mapped[dict] = mapped_column(JSON, nullable=True)
    
    # Conditional display logic (JSON object)
    conditional_logic: Mapped[dict] = mapped_column(JSON, nullable=True)
    
    # Free text controls
    free_text_max_length: Mapped[int] = mapped_column(Integer, nullable=True)
    free_text_justification: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Linked to validated instrument
    validated_instrument: Mapped[str] = mapped_column(String(255), nullable=True)
    
    # Data dictionary
    variable_name: Mapped[str] = mapped_column(String(100), nullable=False)
    variable_type: Mapped[str] = mapped_column(String(50), nullable=False)
    variable_description: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Quality flags
    has_guidance_warning: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    warning_message: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Relationships
    questionnaire: Mapped[Questionnaire] = relationship("Questionnaire", back_populates="questions")


class AuditEpisode(Base, UUIDMixin, TimestampMixin):
    """
    Single patient encounter/episode within an audit.
    One row per patient per audit submission.
    """
    __tablename__ = "audit_episodes"
    
    # Parent audit
    audit_id: Mapped[str] = mapped_column(String(36), ForeignKey("audits.id"), nullable=False, index=True)
    
    # Questionnaire version used
    questionnaire_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("questionnaires.id"),
        nullable=False,
    )
    questionnaire_version: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Site and submitter
    site_id: Mapped[str] = mapped_column(String(36), ForeignKey("sites.id"), nullable=False, index=True)
    submitted_by_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)
    
    # Episode identification
    episode_code: Mapped[str] = mapped_column(String(100), nullable=True)  # Site-specific ID
    pseudonym: Mapped[str] = mapped_column(String(64), nullable=True, index=True)  # For linkage
    
    # Status
    is_validated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    validation_errors: Mapped[dict] = mapped_column(JSON, nullable=True)
    
    # Consent (if required)
    consent_obtained: Mapped[bool] = mapped_column(Boolean, nullable=True)
    consent_date: Mapped[datetime] = mapped_column(nullable=True)
    
    # Responses stored as JSON (flexible schema)
    responses: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    # Derived metrics
    derived_metrics: Mapped[dict] = mapped_column(JSON, nullable=True)
    
    # Relationships
    audit: Mapped[Audit] = relationship("Audit", back_populates="episodes")


class DPIA(Base, UUIDMixin, TimestampMixin):
    """
    Data Protection Impact Assessment for an audit.
    """
    __tablename__ = "dpias"
    
    # Parent audit
    audit_id: Mapped[str] = mapped_column(String(36), ForeignKey("audits.id"), nullable=False)
    
    # Status
    status: Mapped[str] = mapped_column(String(50), default="draft", nullable=False)
    
    # Risk assessment
    risk_score: Mapped[int] = mapped_column(Integer, nullable=True)
    risk_level: Mapped[str] = mapped_column(String(50), nullable=True)
    
    # Assessment details (stored as structured JSON)
    assessment_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    # Approval
    approved_by_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[datetime] = mapped_column(nullable=True)
    dpo_reviewed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    dpo_comments: Mapped[str] = mapped_column(Text, nullable=True)


class DataExport(Base, UUIDMixin, TimestampMixin):
    """
    Track data exports for audit trail.
    """
    __tablename__ = "data_exports"
    
    # Audit and user
    audit_id: Mapped[str] = mapped_column(String(36), ForeignKey("audits.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    
    # Export details
    export_type: Mapped[str] = mapped_column(String(50), nullable=False)  # csv, json, excel
    records_count: Mapped[int] = mapped_column(Integer, nullable=False)
    contains_pii: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Justification
    justification: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Approval
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    approved_by_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[datetime] = mapped_column(nullable=True)
    
    # File details
    file_path: Mapped[str] = mapped_column(String(500), nullable=True)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=True)
    download_url: Mapped[str] = mapped_column(String(500), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(nullable=True)
    
    # Access tracking
    download_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_downloaded_at: Mapped[datetime] = mapped_column(nullable=True)
