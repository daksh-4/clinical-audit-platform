"""
User and authentication models.
"""
from sqlalchemy import String, Boolean, Enum as SQLEnum, Table, Column, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from datetime import datetime
import enum

from app.db.base import Base, TimestampMixin, UUIDMixin


class UserRole(str, enum.Enum):
    """User roles for RBAC."""
    PUBLIC = "public"
    REGISTERED = "registered"
    CLINICIAN = "clinician"
    AUDIT_LEAD = "audit_lead"
    QI_TEAM = "qi_team"
    GOVERNANCE = "governance"
    ADMIN = "admin"
    DPO = "dpo"


class MFAMethod(str, enum.Enum):
    """Multi-factor authentication methods."""
    NONE = "none"
    TOTP = "totp"
    SMS = "sms"
    EMAIL = "email"


# Association table for many-to-many user-site relationship
user_sites = Table(
    "user_sites",
    Base.metadata,
    Column("user_id", String(36), ForeignKey("users.id"), primary_key=True),
    Column("site_id", String(36), ForeignKey("sites.id"), primary_key=True),
)


class User(Base, UUIDMixin, TimestampMixin):
    """
    User model for authentication and authorization.
    """
    __tablename__ = "users"
    
    # Basic information
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Role and status
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole),
        default=UserRole.REGISTERED,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # MFA
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    mfa_method: Mapped[MFAMethod] = mapped_column(
        SQLEnum(MFAMethod),
        default=MFAMethod.NONE,
        nullable=False,
    )
    mfa_secret: Mapped[str] = mapped_column(String(255), nullable=True)
    
    # NHS Login integration
    nhs_login_id: Mapped[str] = mapped_column(String(255), nullable=True, unique=True)
    
    # Training
    last_ig_training: Mapped[datetime] = mapped_column(nullable=True)
    
    # Relationships
    sites: Mapped[List["Site"]] = relationship(
        "Site",
        secondary=user_sites,
        back_populates="users",
    )
    owned_audits: Mapped[List["Audit"]] = relationship(
        "Audit",
        back_populates="owner",
        foreign_keys="Audit.owner_id",
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog",
        back_populates="user",
    )


class Site(Base, UUIDMixin, TimestampMixin):
    """
    Healthcare site/organization model.
    """
    __tablename__ = "sites"
    
    # Basic information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    
    # Location
    address: Mapped[str] = mapped_column(String(500), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=True)
    postcode: Mapped[str] = mapped_column(String(20), nullable=True)
    region: Mapped[str] = mapped_column(String(100), nullable=True)
    
    # Organization details
    organization_type: Mapped[str] = mapped_column(String(100), nullable=True)
    parent_organization: Mapped[str] = mapped_column(String(255), nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relationships
    users: Mapped[List[User]] = relationship(
        "User",
        secondary=user_sites,
        back_populates="sites",
    )


class AuditLog(Base, UUIDMixin, TimestampMixin):
    """
    Immutable audit trail for all data access and modifications.
    """
    __tablename__ = "audit_logs"
    
    # Who
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    
    # What
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_id: Mapped[str] = mapped_column(String(36), nullable=False)
    
    # When (created_at from TimestampMixin)
    
    # Where
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str] = mapped_column(String(500), nullable=True)
    
    # Details
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    details: Mapped[dict] = mapped_column(JSON, nullable=True)  # JSON field
    
    # Sensitive data flag
    contains_pii: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    records_accessed: Mapped[int] = mapped_column(nullable=True)
    
    # Justification for access
    justification: Mapped[str] = mapped_column(String(500), nullable=True)
    
    # Relationships
    user: Mapped[User] = relationship("User", back_populates="audit_logs")


class TrainingRecord(Base, UUIDMixin, TimestampMixin):
    """
    Track user training completion and expiry.
    """
    __tablename__ = "training_records"
    
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    module_name: Mapped[str] = mapped_column(String(100), nullable=False)
    completed_date: Mapped[datetime] = mapped_column(nullable=False)
    expiry_date: Mapped[datetime] = mapped_column(nullable=True)
    score: Mapped[int] = mapped_column(nullable=True)
    certificate_url: Mapped[str] = mapped_column(String(500), nullable=True)
