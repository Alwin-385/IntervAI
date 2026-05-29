"""Celery application configuration (Phase 18)."""

from celery import Celery
from celery.signals import task_postrun, task_prerun, worker_process_init

from app.core.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)

celery_app = Celery(
    "ai_interview_intelligence",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_default_queue="default",
    task_routes={
        "resume.extract": {"queue": "resume"},
        "jobs.resume_extraction": {"queue": "resume"},
        "jobs.resume_analysis": {"queue": "resume"},
        "jobs.question_generation": {"queue": "interview"},
        "jobs.transcription": {"queue": "interview"},
        "jobs.answer_evaluation": {"queue": "ai"},
        "jobs.roadmap_generation": {"queue": "ai"},
    },
    task_soft_time_limit=300,
    task_time_limit=360,
    worker_max_tasks_per_child=50,
    result_expires=86_400,
)

celery_app.autodiscover_tasks(["app.workers.tasks"])


@worker_process_init.connect
def _init_worker_db(**_kwargs) -> None:
    from app.core.database import db_manager

    db_manager.init(settings)


@task_prerun.connect
def _task_prerun(sender=None, task_id=None, task=None, **kwargs):
    logger.info("celery_task_prerun", task_name=sender, celery_task_id=task_id)


@task_postrun.connect
def _task_postrun(sender=None, task_id=None, state=None, **kwargs):
    logger.info("celery_task_postrun", task_name=sender, celery_task_id=task_id, state=state)
