from fastapi import Request, status
from fastapi.responses import JSONResponse

class AppException(Exception):
    def __init__(self, status_code: int, message: str, details: str = None):
        self.status_code = status_code
        self.message = message
        self.details = details

async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.message,
                "details": exc.details
            }
        }
    )

class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found", details: str = None):
        super().__init__(status.HTTP_404_NOT_FOUND, message, details)

class UnauthorizedException(AppException):
    def __init__(self, message: str = "Unauthorized", details: str = None):
        super().__init__(status.HTTP_401_UNAUTHORIZED, message, details)

class ForbiddenException(AppException):
    def __init__(self, message: str = "Forbidden", details: str = None):
        super().__init__(status.HTTP_403_FORBIDDEN, message, details)
