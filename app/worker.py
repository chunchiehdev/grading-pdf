from celery import Celery
from markitdown import MarkItDown
from typing import Dict, Any
import io
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Celery configuration
celery_app = Celery(
    'pdf_parser',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# Configure Celery for high concurrency
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    worker_prefetch_multiplier=1,  # Important for fair task distribution
    task_acks_late=True,  # Acknowledge tasks after completion
    worker_max_tasks_per_child=1000,  # Restart worker after 1000 tasks to prevent memory leaks
)

# Initialize PDF parser
md = MarkItDown()


@celery_app.task
def parse_pdf_task(file_data: bytes, user_id: str, file_id: str = None) -> Dict[str, Any]:
    """
    Parse PDF content to markdown
    """
    try:
        # Convert bytes to stream
        file_stream = io.BytesIO(file_data)
        
        # Parse using MarkItDown
        result = md.convert_stream(file_stream)
        
        return {
            "status": "success",
            "content": result.text_content,
            "user_id": user_id,
            "file_id": file_id,
            "error": None
        }
        
    except Exception as e:
        logger.error(f"PDF parsing failed: {str(e)}")
        return {
            "status": "failed",
            "content": None,
            "user_id": user_id,
            "file_id": file_id,
            "error": str(e)
        } 