"""
Custom exception handlers
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger(__name__)


class VirtueAPIException(Exception):
    """Base exception for Virtue API"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ModelNotAvailableException(VirtueAPIException):
    """Exception raised when ML model is not available"""
    def __init__(self, message: str = "Model not available"):
        super().__init__(message, 503)


class ImageProcessingException(VirtueAPIException):
    """Exception raised during image processing"""
    def __init__(self, message: str = "Image processing failed"):
        super().__init__(message, 422)


class VirtualTryOnException(VirtueAPIException):
    """Exception raised during virtual try-on process"""
    def __init__(self, message: str = "Virtual try-on failed"):
        super().__init__(message, 500)


def setup_exception_handlers(app: FastAPI):
    """Setup custom exception handlers"""
    
    @app.exception_handler(VirtueAPIException)
    async def virtue_api_exception_handler(request: Request, exc: VirtueAPIException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.__class__.__name__,
                "message": exc.message,
                "status_code": exc.status_code
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "error": "ValidationError",
                "message": "Request validation failed",
                "details": exc.errors()
            }
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTPException",
                "message": exc.detail,
                "status_code": exc.status_code
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "InternalServerError",
                "message": "An unexpected error occurred",
                "status_code": 500
            }
        )
