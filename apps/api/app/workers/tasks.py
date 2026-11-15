from app.workers.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name="app.workers.tasks.parse_document")
def parse_document(document_id: str, user_id: str):
    logger.info(f"Parsing document {document_id} for user {user_id}")
    return {"status": "completed", "document_id": document_id}


@celery_app.task(name="app.workers.tasks.generate_twin")
def generate_twin(user_id: str):
    logger.info(f"Generating career twin for user {user_id}")
    return {"status": "completed", "user_id": user_id}


@celery_app.task(name="app.workers.tasks.fetch_market_data")
def fetch_market_data(region: str = "global"):
    logger.info(f"Fetching market data for region {region}")
    return {"status": "completed", "region": region}
