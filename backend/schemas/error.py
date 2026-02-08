"""
Error schemas for the Todo App backend API
"""
from typing import Optional
from pydantic import BaseModel


class ErrorDetails(BaseModel):
    """
    Schema for error details in responses
    """
    loc: Optional[list] = None
    msg: Optional[str] = None
    type: Optional[str] = None


class ErrorResponse(BaseModel):
    """
    Schema for structured error responses
    """
    code: str
    message: str
    details: Optional[list[ErrorDetails]] = None


class ValidationErrorResponse(BaseModel):
    """
    Schema for validation error responses
    """
    detail: list[ErrorDetails]