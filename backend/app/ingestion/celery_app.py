import os
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "pmis_ingestion_engine",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=240,
    worker_concurrency=4,
    beat_schedule={
        "expiry-sweep-every-15-min": {
            "task": "app.ingestion.tasks.expiry_check_task",
            "schedule": 900.0,
        },
        "default-source-polling-every-30-min": {
            "task": "app.ingestion.tasks.poll_all_enabled_sources_task",
            "schedule": 1800.0,
        }
    }
)
