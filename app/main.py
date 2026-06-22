from app.core.exceptions import AppException
import contextlib
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables from project root .env (repo_root is three levels up from this file)
repo_root = Path(__file__).resolve().parents[3]
load_dotenv(repo_root / ".env")

# Core config values
DATABASE_URL = os.getenv("DATABASE_URL")
PROJECT_NAME = os.getenv("PROJECT_NAME", "Carmel Kinneret Server")
API_V1_STR = os.getenv("API_V1_STR", "/api")

# Exception handlers import (single line)
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_async_session
from app.api.router import api_router


app = FastAPI(
    title=PROJECT_NAME,
    openapi_url=f"{API_V1_STR}/openapi.json",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include API Router
app.include_router(api_router, prefix=API_V1_STR)

@app.get("/")
async def root():
    return {"message": f"Welcome to {PROJECT_NAME} API"}


@app.get("/db/ping")
async def db_ping(db: AsyncSession = Depends(get_async_session)):
    """Health-check endpoint that verifies DB connectivity.

    Executes a lightweight ``SELECT 1`` query. Returns ``{"status": "ok", "result": 1}``
    on success or ``{"status": "error", "detail": <error>}`` on failure.
    """
    try:
        result = await db.execute(text("SELECT 1"))
        return {"status": "ok", "result": result.scalar()}
    except Exception as exc:
        return {"status": "error", "detail": str(exc)}
