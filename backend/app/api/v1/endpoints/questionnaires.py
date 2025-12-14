"""
Questionnaire management endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.db.session import get_db
from app.models.user import User
from app.models.audit import Audit, Questionnaire, Question
from app.schemas.audit import QuestionnaireCreate, QuestionnaireResponse
from app.api.v1.endpoints.auth import get_current_user


router = APIRouter()


@router.post("/{audit_id}/questionnaires", response_model=QuestionnaireResponse, status_code=status.HTTP_201_CREATED)
async def create_questionnaire(
    audit_id: str,
    questionnaire_data: QuestionnaireCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new questionnaire version for an audit.
    """
    # Get audit
    result = await db.execute(select(Audit).where(Audit.id == audit_id))
    audit = result.scalar_one_or_none()
    
    if not audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit not found",
        )
    
    # Only owner can create questionnaires
    if audit.owner_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only audit owner can create questionnaires",
        )
    
    # Get latest version number
    result = await db.execute(
        select(Questionnaire)
        .where(Questionnaire.audit_id == audit_id)
        .order_by(Questionnaire.version.desc())
    )
    latest = result.first()
    new_version = (latest[0].version + 1) if latest else 1
    
    # Create questionnaire
    questionnaire = Questionnaire(
        audit_id=audit_id,
        version=new_version,
        title=questionnaire_data.title,
        description=questionnaire_data.description,
    )
    
    db.add(questionnaire)
    await db.flush()  # Get questionnaire ID
    
    # Create questions
    for idx, question_data in enumerate(questionnaire_data.questions):
        question = Question(
            questionnaire_id=str(questionnaire.id),
            order_index=idx,
            **question_data.model_dump(),
        )
        db.add(question)
    
    await db.commit()
    await db.refresh(questionnaire)
    
    # Load questions relationship
    result = await db.execute(
        select(Questionnaire)
        .where(Questionnaire.id == str(questionnaire.id))
    )
    questionnaire = result.scalar_one()
    
    return questionnaire


@router.get("/{audit_id}/questionnaires", response_model=List[QuestionnaireResponse])
async def list_questionnaires(
    audit_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all questionnaire versions for an audit.
    """
    # Get audit
    result = await db.execute(select(Audit).where(Audit.id == audit_id))
    audit = result.scalar_one_or_none()
    
    if not audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit not found",
        )
    
    # Get questionnaires
    result = await db.execute(
        select(Questionnaire)
        .where(Questionnaire.audit_id == audit_id)
        .order_by(Questionnaire.version.desc())
    )
    questionnaires = result.scalars().all()
    
    return questionnaires


@router.get("/{audit_id}/questionnaires/{version}", response_model=QuestionnaireResponse)
async def get_questionnaire(
    audit_id: str,
    version: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific questionnaire version.
    """
    result = await db.execute(
        select(Questionnaire)
        .where(
            Questionnaire.audit_id == audit_id,
            Questionnaire.version == version,
        )
    )
    questionnaire = result.scalar_one_or_none()
    
    if not questionnaire:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Questionnaire not found",
        )
    
    return questionnaire
