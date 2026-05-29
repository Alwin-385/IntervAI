"""API v1 route aggregator."""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    analytics,
    answers,
    dashboard,
    health,
    interview_sessions,
    interviews,
    jobs,
    me,
    resumes,
    roadmap_engine,
    roadmaps,
    speech,
    users,
    weak_areas,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(jobs.router)
api_router.include_router(me.router)
api_router.include_router(dashboard.router)
api_router.include_router(analytics.router)
api_router.include_router(users.router)
api_router.include_router(resumes.router)
api_router.include_router(interview_sessions.router)
api_router.include_router(interviews.router)
api_router.include_router(speech.router)
api_router.include_router(answers.router)
api_router.include_router(weak_areas.router)
api_router.include_router(roadmaps.router)
api_router.include_router(roadmap_engine.router)
