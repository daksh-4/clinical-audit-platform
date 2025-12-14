"""
Main API router combining all endpoint modules.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, audits, questionnaires, episodes, users


api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(audits.router, prefix="/audits", tags=["audits"])
api_router.include_router(questionnaires.router, prefix="/questionnaires", tags=["questionnaires"])
api_router.include_router(episodes.router, prefix="/episodes", tags=["episodes"])
