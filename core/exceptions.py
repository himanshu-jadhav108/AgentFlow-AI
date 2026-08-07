"""Global error handlers and custom exceptions for the FastAPI application."""

from typing import Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from models.responses import ErrorResponse
from core.logger import logger


class AppException(Exception):
    """Base application exception for raising handled errors with specific HTTP status codes."""

    def __init__(
        self,
        detail: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        error_code: Optional[str] = None,
    ) -> None:
        self.detail = detail
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(detail)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handles custom AppException and returns formatted JSON response."""
    logger.error(f"AppException raised on {request.method} {request.url.path}: {exc.detail}")
    response_body = ErrorResponse(
        detail=exc.detail,
        status_code=exc.status_code,
        error_code=exc.error_code,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=response_body.model_dump(),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handles pydantic validation exceptions, formatting them into standard ErrorResponse structures."""
    logger.warning(f"Request validation failed on {request.method} {request.url.path}")
    
    # Standardize details
    error_list = []
    for err in exc.errors():
        loc_str = ".".join(str(x) for x in err.get("loc", []))
        msg = err.get("msg", "Unknown error")
        error_list.append(f"Field '{loc_str}' - {msg}")
    
    joined_details = " | ".join(error_list)
    response_body = ErrorResponse(
        detail=f"Validation failed: {joined_details}",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error_code="VALIDATION_ERROR",
        meta={"errors": exc.errors()},
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response_body.model_dump(),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global generic fallback exception handler for unhandled errors (HTTP 500)."""
    logger.exception(f"Unhandled system exception raised on {request.method} {request.url.path}: {exc}")
    response_body = ErrorResponse(
        detail="An internal server error occurred.",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code="INTERNAL_SERVER_ERROR",
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response_body.model_dump(),
    )
