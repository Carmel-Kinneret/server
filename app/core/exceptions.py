from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

class AppException(Exception):
    def __init__(self, status_code: int, message: str, details: str = None):
        self.status_code = status_code
        self.message = message
        self.details = details

async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "code": exc.status_code,
            "message": exc.message
        }
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "code": exc.status_code,
            "message": exc.detail
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    message = "Validation error"
    if errors:
        first_err = errors[0]
        loc = ".".join(str(l) for l in first_err.get("loc", []))
        msg = first_err.get("msg", "invalid value")
        message = f"Validation error at {loc}: {msg}"
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": True,
            "code": status.HTTP_400_BAD_REQUEST,
            "message": message
        }
    )

async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": f"Internal server error: {str(exc)}"
        }
    )

class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found or has been removed.", details: str = None):
        super().__init__(status.HTTP_404_NOT_FOUND, message, details)

class UnauthorizedException(AppException):
    def __init__(self, message: str = "Unauthorized", details: str = None):
        super().__init__(status.HTTP_401_UNAUTHORIZED, message, details)

class ForbiddenException(AppException):
    def __init__(self, message: str = "Forbidden", details: str = None):
        super().__init__(status.HTTP_403_FORBIDDEN, message, details)

