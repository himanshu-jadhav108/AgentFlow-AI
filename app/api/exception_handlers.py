"""Custom exceptions and reusable exception handlers returning standardized JSON errors."""

from typing import Any, Dict

from fastapi import FastAPI, Request, status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse

from core.logger import logger


class ModelLoadException(Exception):
    """Exception raised when local model loading fails."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class RetrievalException(Exception):
    """Exception raised during vector index retrieval failures."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class GraphException(Exception):
    """Exception raised when LangGraph workflow execution fails."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


def format_error_response(
    code: str, message: str, details: Any = None, status_code: int = 500
) -> Dict[str, Any]:
    """Helper to compile standard API error JSON bodies, supporting legacy fields."""
    return {
        "success": False,
        "detail": message,
        "status_code": status_code,
        "error_code": code,
        "meta": details or {},
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
        },
    }


async def request_validation_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Formats Pydantic/FastAPI request validation errors."""
    logger.warning(f"Request validation failed on {request.method} {request.url.path}")

    error_list = []
    for err in exc.errors():
        loc_str = ".".join(str(x) for x in err.get("loc", []))
        msg = err.get("msg", "Validation mismatch")
        error_list.append({"field": loc_str, "issue": msg})

    joined_msgs = ", ".join(f"{x['field']}: {x['issue']}" for x in error_list)
    content = format_error_response(
        code="VALIDATION_ERROR",
        message=f"Validation failed: {joined_msgs}",
        details={"errors": exc.errors()},
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=content
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Formats standard HTTPExceptions (e.g. 404, 401)."""
    logger.warning(
        f"HTTPException ({exc.status_code}) on {request.method} {request.url.path}: {exc.detail}"
    )
    content = format_error_response(
        code=f"HTTP_{exc.status_code}_ERROR",
        message=exc.detail,
        status_code=exc.status_code,
    )
    return JSONResponse(status_code=exc.status_code, content=content)


async def model_load_handler(request: Request, exc: ModelLoadException) -> JSONResponse:
    """Formats local LLM/embedding weight loading failures."""
    logger.error(
        f"Model load failure on {request.method} {request.url.path}: {exc.message}"
    )
    content = format_error_response(
        code="MODEL_LOAD_ERROR",
        message="Failed to load local AI model weights into RAM.",
        details={"error_message": exc.message},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=content
    )


async def retrieval_handler(request: Request, exc: RetrievalException) -> JSONResponse:
    """Formats FAISS index retrieval failures."""
    logger.error(
        f"Vector search failure on {request.method} {request.url.path}: {exc.message}"
    )
    content = format_error_response(
        code="RETRIEVAL_ERROR",
        message="Error executing similarity search inside the local vector store.",
        details={"error_message": exc.message},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=content
    )


async def graph_handler(request: Request, exc: GraphException) -> JSONResponse:
    """Formats LangGraph execution failures."""
    logger.error(
        f"Workflow execution failure on {request.method} {request.url.path}: {exc.message}"
    )
    content = format_error_response(
        code="GRAPH_EXECUTION_ERROR",
        message="Failed to execute graph workflow states.",
        details={"error_message": exc.message},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=content
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Unhandled generic exception fallback (never exposes internals)."""
    logger.exception(
        f"Unhandled system error on {request.method} {request.url.path}: {exc}"
    )
    content = format_error_response(
        code="INTERNAL_SERVER_ERROR",
        message="An unexpected server error occurred.",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=content
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Registers standard handlers globally on the FastAPI application."""
    app.add_exception_handler(RequestValidationError, request_validation_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(ModelLoadException, model_load_handler)
    app.add_exception_handler(RetrievalException, retrieval_handler)
    app.add_exception_handler(GraphException, graph_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
