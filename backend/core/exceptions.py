from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Union, Dict, Any


async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Global exception handler for HTTPException
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


async def validation_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for validation errors
    """
    # This would typically handle RequestValidationError and ValidationError
    # For now, we'll return a generic error format
    return JSONResponse(
        status_code=422,
        content={
            "detail": [
                {
                    "loc": ["request"],
                    "msg": str(exc),
                    "type": "validation_error"
                }
            ]
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for general exceptions
    """
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )