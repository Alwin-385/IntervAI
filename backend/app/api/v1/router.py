"""API v1 route aggregator."""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    health,
    interview_sessions,
    resumes,
    roadmaps,
    users,
    weak_areas,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(users.router)
api_router.include_router(resumes.router)
api_router.include_router(interview_sessions.router)
api_router.include_router(weak_areas.router)
api_router.include_router(roadmaps.router)
