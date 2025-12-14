"""
Pydantic schemas for User entities.
"""
from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Optional
from app.models.user import UserRole, MFAMethod


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 12:
            raise ValueError("Password must be at least 12 characters")
        return v


class UserUpdate(BaseModel):
    """Schema for updating user details."""
    full_name: Optional[str] = None
    mfa_enabled: Optional[bool] = None
    mfa_method: Optional[MFAMethod] = None


class UserInDB(UserBase):
    """Schema for user as stored in database."""
    id: str
    role: UserRole
    is_active: bool
    is_verified: bool
    mfa_enabled: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserResponse(UserInDB):
    """Schema for user in API responses."""
    pass


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Data encoded in JWT token."""
    user_id: str
    email: str
    role: UserRole
