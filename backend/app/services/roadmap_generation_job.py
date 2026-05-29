"""Background worker for roadmap generation."""

from __future__ import annotations

import asyncio
from uuid import UUID

from app.services.background_job_sync import sync_job_update_progress


def execute_roadmap_generation_sync(payload: dict) -> dict:
    from app.core.database import db_manager
    from app.repositories.analytics_queries import AnalyticsQueryRepository
    from app.repositories.roadmap import RoadmapRepository
    from app.repositories.user import UserRepository
    from app.schemas.roadmap_engine import GenerateRoadmapRequest
    from app.services.roadmap_engine import RoadmapEngineService

    job_id = payload.get("job_id")
    user_id = UUID(payload["user_id"])
    target_role = payload.get("target_role")

    async def _run():
        async with db_manager.session_factory() as session:
            svc = RoadmapEngineService(
                RoadmapRepository(session),
                AnalyticsQueryRepository(session),
                UserRepository(session),
            )
            return await svc.generate_roadmap(
                user_id,
                GenerateRoadmapRequest(target_role=target_role, force_regenerate=True),
            )

    loop = asyncio.new_event_loop()
    try:
        if job_id:
            sync_job_update_progress(job_id, percent=40, message="Analyzing performance…")
        roadmap = loop.run_until_complete(_run())
    finally:
        loop.close()

    return {
        "roadmap_id": str(roadmap.id),
        "total_items": roadmap.total_items,
        "status": "completed",
    }
