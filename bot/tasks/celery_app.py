"""Celery Application Setup for Asynchronous PDF Processing.

Uses Redis as the message broker and result backend with auto-discovery of tasks.
Configures periodic beat schedule to purge temporary files older than 24 hours.
"""
from celery import Celery
from celery.schedules import crontab
from bot.config import settings

celery_app = Celery(
    "persian_pdf_bot",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["bot.tasks.celery_worker"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Tehran",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=900,  # 15 minutes max per task
    task_soft_time_limit=840,
    worker_prefetch_multiplier=1,  # Prevent worker from hogging large files
    worker_max_tasks_per_child=50,  # Prevent memory leaks from OCR/PyMuPDF
    beat_schedule={
        "purge-expired-temp-files-every-hour": {
            "task": "bot.tasks.celery_worker.purge_expired_files_task",
            "schedule": crontab(minute=0),  # Run every hour
        },
    }
)
