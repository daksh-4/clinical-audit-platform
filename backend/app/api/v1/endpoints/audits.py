"""
Audit management endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.db.session import get_db
from app.models.user import User
from app.models.audit import Audit, AuditStatus
from app.schemas.audit import AuditCreate, AuditUpdate, AuditResponse
from app.api.v1.endpoints.auth import get_current_user


router = APIRouter()


@router.post("/", response_model=AuditResponse, status_code=status.HTTP_201_CREATED)
async def create_audit(
    audit_data: AuditCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new audit.
    """
    from app.models.user import UserRole
    
    # Only registered users and above can create audits
    if current_user.role == UserRole.PUBLIC:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Must be registered to create audits",
        )
    
    # Create audit
    audit = Audit(
        **audit_data.model_dump(),
        owner_id=str(current_user.id),
        status=AuditStatus.DRAFT,
    )
    
    db.add(audit)
    await db.commit()
    await db.refresh(audit)
    
    return audit


@router.get("/", response_model=List[AuditResponse])
async def list_audits(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List audits accessible to current user.
    """
    from app.models.user import UserRole
    
    # Admins and governance see all audits
    if current_user.role in [UserRole.ADMIN, UserRole.GOVERNANCE]:
        result = await db.execute(select(Audit).offset(skip).limit(limit))
    else:
        # Users see their own audits and public audits
        result = await db.execute(
            select(Audit)
            .where(
                (Audit.owner_id == str(current_user.id)) | 
                (Audit.is_public == True)
            )
            .offset(skip)
            .limit(limit)
        )
    
    audits = result.scalars().all()
    return audits


@router.get("/{audit_id}", response_model=AuditResponse)
async def get_audit(
    audit_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get audit by ID.
    """
    result = await db.execute(select(Audit).where(Audit.id == audit_id))
    audit = result.scalar_one_or_none()
    
    if not audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit not found",
        )
    
    # Check access
    from app.models.user import UserRole
    if (
        audit.owner_id != str(current_user.id) and
        not audit.is_public and
        current_user.role not in [UserRole.ADMIN, UserRole.GOVERNANCE]
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this audit",
        )
    
    return audit


@router.patch("/{audit_id}", response_model=AuditResponse)
async def update_audit(
    audit_id: str,
    audit_update: AuditUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update audit details.
    """
    result = await db.execute(select(Audit).where(Audit.id == audit_id))
    audit = result.scalar_one_or_none()
    
    if not audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit not found",
        )
    
    # Only owner can update
    if audit.owner_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only audit owner can update",
        )
    
    # Update fields
    update_data = audit_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(audit, field, value)
    
    await db.commit()
    await db.refresh(audit)
    
    return audit


@router.delete("/{audit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_audit(
    audit_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete an audit (only if in DRAFT status).
    """
    result = await db.execute(select(Audit).where(Audit.id == audit_id))
    audit = result.scalar_one_or_none()
    
    if not audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit not found",
        )
    
    # Only owner can delete
    if audit.owner_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only audit owner can delete",
        )
    
    # Can only delete drafts
    if audit.status != AuditStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only delete audits in DRAFT status",
        )
    
    await db.delete(audit)
    await db.commit()
