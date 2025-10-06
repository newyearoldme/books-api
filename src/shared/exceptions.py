import logging
from typing import Any

from fastapi import HTTPException, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("src")


class BaseAPIException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str | None = None,
        extra_data: dict[str, Any] | None = None,
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code or f"ERR_{status_code}"
        self.extra_data = extra_data or {}


class NotFoundException(BaseAPIException):
    def __init__(
        self,
        detail: str = "Resource not found",
        resource_type: str | None = None,
        resource_id: Any | None = None,
    ):
        extra_data = {}
        if resource_type:
            extra_data["resource_type"] = resource_type
        if resource_id is not None:
            extra_data["resource_id"] = resource_id

        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="NOT_FOUND",
            extra_data=extra_data,
        )


class ValidationException(BaseAPIException):
    def __init__(
        self, detail: str = "Validation error", field_errors: dict[str, str] = None
    ):
        extra_data = {"field_errors": field_errors} if field_errors else {}
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="VALIDATION_ERROR",
            extra_data=extra_data,
        )


class AlreadyExistsException(BaseAPIException):
    def __init__(
        self,
        detail: str = "Resource already exists",
        resource_type: str | None = None,
        field: str | None = None,
        value: Any | None = None,
    ):
        extra_data = {}
        if resource_type:
            extra_data["resource_type"] = resource_type
        if field:
            extra_data["field"] = field
        if value is not None:
            extra_data["value"] = value

        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code="ALREADY_EXISTS",
            extra_data=extra_data,
        )


class UnauthorizedException(BaseAPIException):
    def __init__(self, detail: str = "Not authenticated"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="UNAUTHORIZED",
        )


class ForbiddenException(BaseAPIException):
    def __init__(self, detail: str = "Access forbidden"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN, detail=detail, error_code="FORBIDDEN"
        )


class InternalServerErrorException(BaseAPIException):
    def __init__(self, detail: str = "Internal server error"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="INTERNAL_ERROR",
        )


async def global_exception_handler(request: Request, exc: Exception):
    """Обрабатывает все необработанные исключения"""
    if isinstance(exc, BaseAPIException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "error_code": exc.error_code,
                **exc.extra_data,
            },
        )
    elif isinstance(exc, HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    else:
        logger.error(f"Unhandled exception: {exc}", exc_info=True)

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error", "error_code": "INTERNAL_ERROR"},
        )
