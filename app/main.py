from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import logging

from app.models import ParseResponse, ParseResult, TaskStatus
from app.worker import celery_app, parse_pdf_task
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="PDF Parser Service",
    description="A service for parsing PDF files to Markdown using MarkItDown",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/parse", response_model=ParseResponse)
async def parse_pdf_async(
    file: UploadFile = File(...),
    user_id: str = "default",
    file_id: Optional[str] = None
):
    """Parse PDF file asynchronously"""
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Check file size
    file_content = await file.read()
    if len(file_content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413, 
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    try:
        # Submit task to Celery
        task = parse_pdf_task.delay(file_content, user_id, file_id)
        
        return ParseResponse(
            task_id=task.id,
            status=TaskStatus.PENDING,
            message="PDF parsing task submitted successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to submit PDF parsing task: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to submit parsing task: {str(e)}")


@app.get("/task/{task_id}", response_model=ParseResult)
async def get_task_result(task_id: str):
    """Get the result of a parsing task"""
    try:
        result = celery_app.AsyncResult(task_id)
        
        if result.state == 'PENDING':
            return ParseResult(
                task_id=task_id,
                status=TaskStatus.PENDING,
                content=None,
                user_id="",
                file_id=None,
                error=None
            )
        elif result.state == 'SUCCESS':
            task_result = result.result
            return ParseResult(
                task_id=task_id,
                status=TaskStatus.SUCCESS,
                content=task_result.get("content"),
                user_id=task_result.get("user_id"),
                file_id=task_result.get("file_id"),
                error=task_result.get("error")
            )
        elif result.state == 'FAILURE':
            return ParseResult(
                task_id=task_id,
                status=TaskStatus.FAILED,
                content=None,
                user_id="",
                file_id=None,
                error=str(result.info)
            )
        else:
            return ParseResult(
                task_id=task_id,
                status=TaskStatus.PROCESSING,
                content=None,
                user_id="",
                file_id=None,
                error=None
            )
            
    except Exception as e:
        logger.error(f"Failed to get task result for {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get task result: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "pdf-parser"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "PDF Parser Service",
        "docs": "/docs",
        "health": "/health"
    } 