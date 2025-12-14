"""
Data entry endpoints for audit episodes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime

from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.audit import Audit, Questionnaire, AuditEpisode
from app.schemas.audit import EpisodeCreate, EpisodeResponse
from app.api.v1.endpoints.auth import get_current_user


router = APIRouter()


@router.post("/{audit_id}/episodes", response_model=EpisodeResponse, status_code=status.HTTP_201_CREATED)
async def submit_episode(
    audit_id: str,
    episode_data: EpisodeCreate,
    site_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Submit a new audit episode (patient data entry).
    """
    # Verify audit exists and is active
    result = await db.execute(select(Audit).where(Audit.id == audit_id))
    audit = result.scalar_one_or_none()
    
    if not audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit not found",
        )
    
    from app.models.audit import AuditStatus
    if audit.status not in [AuditStatus.ACTIVE]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audit is not active for data collection",
        )
    
    # Only clinicians and above can submit data
    if current_user.role == UserRole.PUBLIC:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Must have clinician role to submit data",
        )
    
    # Get latest published questionnaire
    result = await db.execute(
        select(Questionnaire)
        .where(
            Questionnaire.audit_id == audit_id,
            Questionnaire.is_published == True,
        )
        .order_by(Questionnaire.version.desc())
    )
    questionnaire = result.first()
    
    if not questionnaire:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No published questionnaire available",
        )
    
    questionnaire = questionnaire[0]
    
    # Create episode
    episode = AuditEpisode(
        audit_id=audit_id,
        questionnaire_id=str(questionnaire.id),
        questionnaire_version=questionnaire.version,
        site_id=site_id,
        submitted_by_id=str(current_user.id),
        submitted_at=datetime.utcnow(),
        episode_code=episode_data.episode_code,
        responses=episode_data.responses,
        consent_obtained=episode_data.consent_obtained,
        consent_date=episode_data.consent_date,
    )
    
    db.add(episode)
    
    # Update audit total episodes
    audit.total_episodes += 1
    
    await db.commit()
    await db.refresh(episode)
    
    return episode


@router.get("/{audit_id}/episodes", response_model=List[EpisodeResponse])
async def list_episodes(
    audit_id: str,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List episodes for an audit.
    """
    # Get audit
    result = await db.execute(select(Audit).where(Audit.id == audit_id))
    audit = result.scalar_one_or_none()
    
    if not audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit not found",
        )
    
    # Check permissions
    if audit.owner_id != str(current_user.id) and current_user.role not in [UserRole.ADMIN, UserRole.GOVERNANCE]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view episodes",
        )
    
    # Get episodes
    result = await db.execute(
        select(AuditEpisode)
        .where(AuditEpisode.audit_id == audit_id)
        .offset(skip)
        .limit(limit)
    )
    episodes = result.scalars().all()
    
    return episodes


@router.get("/{audit_id}/episodes/{episode_id}", response_model=EpisodeResponse)
async def get_episode(
    audit_id: str,
    episode_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific episode.
    """
    result = await db.execute(
        select(AuditEpisode)
        .where(
            AuditEpisode.id == episode_id,
            AuditEpisode.audit_id == audit_id,
        )
    )
    episode = result.scalar_one_or_none()
    
    if not episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Episode not found",
        )
    
    # Check permissions
    result = await db.execute(select(Audit).where(Audit.id == audit_id))
    audit = result.scalar_one_or_none()
    
    if audit.owner_id != str(current_user.id) and current_user.role not in [UserRole.ADMIN, UserRole.GOVERNANCE]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this episode",
        )
    
    return episode
