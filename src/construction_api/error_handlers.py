"""
RFC 9457 Problem Details for HTTP APIs

This module provides RFC 9457 compliant error responses.
See: https://www.rfc-editor.org/rfc/rfc9457.html
"""

from typing import Optional

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ProblemDetail(BaseModel):
    """RFC 9457 Problem Details response."""

    title: str
    status: int
    detail: str
    instance: Optional[str] = None


def create_problem_response(
    title: str,
    status_code: int,
    detail: str,
    instance: Optional[str] = None,
) -> JSONResponse:
    """Create an RFC 9457 compliant problem response."""
    problem = ProblemDetail(
        title=title,
        status=status_code,
        detail=detail,
        instance=instance,
    )
    return JSONResponse(
        status_code=status_code,
        content=problem.model_dump(exclude_none=True),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle FastAPI validation errors with RFC 9457 format."""

    errors = exc.errors()

    # Build a detailed error message
    error_messages = []
    for error in errors:
        loc = " -> ".join(str(x) for x in error["loc"])
        msg = error["msg"]
        error_messages.append(f"{loc}: {msg}")

    detail = "; ".join(error_messages)

    return create_problem_response(
        title="Request Validation Error",
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        detail=detail,
        instance=str(request.url.path),
    )


async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle HTTP exceptions with RFC 9457 format."""
    from fastapi import HTTPException

    if not isinstance(exc, HTTPException):
        raise exc

    # Map status codes to titles
    titles = {
        status.HTTP_400_BAD_REQUEST: "Bad Request",
        status.HTTP_401_UNAUTHORIZED: "Unauthorized",
        status.HTTP_403_FORBIDDEN: "Forbidden",
        status.HTTP_404_NOT_FOUND: "Resource Not Found",
        status.HTTP_409_CONFLICT: "Conflict",
        status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal Server Error",
    }

    return create_problem_response(
        title=titles.get(exc.status_code, "Error"),
        status_code=exc.status_code,
        detail=exc.detail,
        instance=str(request.url.path),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected errors with RFC 9457 format."""

    return create_problem_response(
        title="Internal Server Error",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An unexpected error occurred. Please try again later.",
        instance=str(request.url.path),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers with the FastAPI app."""
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    # Import here to avoid circular imports
    from fastapi import HTTPException

    app.add_exception_handler(HTTPException, http_exception_handler)
