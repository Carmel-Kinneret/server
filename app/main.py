"""Application entry point for the Carmel Kinneret Server.

This module creates the FastAPI application, loads environment variables,
configures CORS, registers global exception handlers, and includes the
router that aggregates all API sub‑routers.

The ``db_ping`` endpoint provides a lightweight health‑check that validates
database connectivity.
"""

# Standard library imports
import os
import contextlib
from pathlib import Path

# Third‑party imports
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# Local imports – exception handlers and database utilities
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)
from app.db.database import get_async_session
from app.api.router import api_router

# ---------------------------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------------------------
# The .env file resides in the project root (three levels up from this file).
repo_root = Path(__file__).resolve().parents[3]
load_dotenv(repo_root / ".env")

# ---------------------------------------------------------------------------
# Core configuration values
# ---------------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")
PROJECT_NAME = os.getenv("PROJECT_NAME", "Carmel Kinneret Server")
API_V1_STR = os.getenv("API_V1_STR", "/api")

# ---------------------------------------------------------------------------
# FastAPI application instance
# ---------------------------------------------------------------------------
app = FastAPI(
    title=PROJECT_NAME,
    openapi_url=f"{API_V1_STR}/openapi.json",
)

# ---------------------------------------------------------------------------
# CORS configuration – allow all origins for development; adjust for prod.
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Register global exception handlers
# ---------------------------------------------------------------------------
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# ---------------------------------------------------------------------------
# Include the aggregated API router
# ---------------------------------------------------------------------------
app.include_router(api_router, prefix=API_V1_STR)

# ---------------------------------------------------------------------------
# Simple health endpoints
# ---------------------------------------------------------------------------
@app.get("/")
async def root() -> dict:
    """Root endpoint returning a welcome message."""
    return {"message": f"Welcome to {PROJECT_NAME} API"}


@app.get("/db/ping")
async def db_ping(db: AsyncSession = Depends(get_async_session)) -> dict:
    """Health‑check endpoint that verifies DB connectivity.

    Executes ``SELECT 1`` and returns ``{"status": "ok", "result": 1}`` on
    success, otherwise returns an error dictionary.
    """
    try:
        result = await db.execute(text("SELECT 1"))
        return {"status": "ok", "result": result.scalar()}
    except Exception as exc:
        return {"status": "error", "detail": str(exc)}
