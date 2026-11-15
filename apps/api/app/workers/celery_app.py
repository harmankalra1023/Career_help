from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "dct_workers",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_routes={
        "app.workers.tasks.parse_document": {"queue": "ingest"},
        "app.workers.tasks.sync_github": {"queue": "ingest"},
        "app.workers.tasks.generate_twin": {"queue": "scoring"},
        "app.workers.tasks.recompute_scores": {"queue": "scoring"},
        "app.workers.tasks.fetch_market_data": {"queue": "market"},
        "app.workers.tasks.generate_dna_narrative": {"queue": "llm"},
    },
)
