from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


# These schemas are already defined in task.py, but we'll add any additional schemas needed
# for API requests/responses that aren't directly related to the Task model

class ErrorMessage(BaseModel):
    """Standard error message response schema"""
    detail: str


class ValidationErrorItem(BaseModel):
    """Schema for a single validation error item"""
    loc: List[str]
    msg: str
    type: str


class ValidationErrorResponse(BaseModel):
    """Schema for validation error response"""
    detail: List[ValidationErrorItem]


class HealthCheckResponse(BaseModel):
    """Schema for health check endpoint response"""
    status: str = "healthy"
    timestamp: datetime


class ApiResponse(BaseModel):
    """Generic API response schema"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None