from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Optional
import logging

from app.models import ParseRequest, ParseResponse, ParseResult, TaskStatus
from app.worker import celery_app, parse_pdf_task
from app.services.pdf_parser import PDFParserService, PDFParsingError

logger = logging.getLogger(__name__)
router = APIRouter()

# For synchronous parsing
pdf_parser = PDFParserService()


@router.post("/parse", response_model=ParseResponse)
async def parse_pdf_async(
    file: UploadFile = File(...),
    user_id: str = None,
    file_id: Optional[str] = None
):
    """
    Parse PDF file asynchronously using Celery
    """
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Submit task to Celery
        task = parse_pdf_task.delay(file_content, user_id, file_id)
        
        logger.info(f"PDF parsing task {task.id} submitted for user {user_id}")
        
        return ParseResponse(
            task_id=task.id,
            status=TaskStatus.PENDING,
            message="PDF parsing task submitted successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to submit PDF parsing task: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to submit parsing task: {str(e)}")


@router.post("/parse/sync", response_model=ParseResult)
async def parse_pdf_sync(
    file: UploadFile = File(...),
    user_id: str = None,
    file_id: Optional[str] = None
):
    """
    Parse PDF file synchronously (for smaller files or testing)
    """
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Parse immediately
        content = pdf_parser.parse_pdf_content(file_content)
        
        return ParseResult(
            task_id="sync",
            status=TaskStatus.SUCCESS,
            content=content,
            user_id=user_id,
            file_id=file_id,
            error=None
        )
        
    except PDFParsingError as e:
        logger.error(f"PDF parsing failed: {str(e)}")
        return ParseResult(
            task_id="sync",
            status=TaskStatus.FAILED,
            content=None,
            user_id=user_id,
            file_id=file_id,
            error=str(e)
        )
        
    except Exception as e:
        logger.error(f"Unexpected error during PDF parsing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Parsing failed: {str(e)}")


@router.get("/task/{task_id}", response_model=ParseResult)
async def get_task_result(task_id: str):
    """
    Get the result of a parsing task
    """
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
            return ParseResult(**task_result)
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


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "pdf-parser"} 