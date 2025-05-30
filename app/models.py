from pydantic import BaseModel
from typing import Optional
from enum import Enum


class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"


class ParseRequest(BaseModel):
    user_id: str
    file_id: Optional[str] = None


class ParseResponse(BaseModel):
    task_id: str
    status: TaskStatus
    message: str


class ParseResult(BaseModel):
    task_id: str
    status: TaskStatus
    content: Optional[str] = None
    user_id: str
    file_id: Optional[str] = None
    error: Optional[str] = None 