import contextlib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables from project root .env
repo_root = Path(__file__).resolve().parents[3]
load_dotenv(repo_root / ".env")

# Core config values
PROJECT_NAME = os.getenv("PROJECT_NAME", "Carmel Kinneret Server")
API_V1_STR = os.getenv("API_V1_STR", "/api")

from app.core.exceptions import (
    AppException,
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)
from app.api.router import api_router
from app.db.database import engine
from app.models.base import Base

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup - normally done by Alembic, but since we are not using it,
    # we can create tables here for dev purposes if needed, 
    # though it's better to run a script. We'll leave it as a comment.
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    yield
    # Teardown
    await engine.dispose()

app = FastAPI(
    title=PROJECT_NAME,
    openapi_url=f"{API_V1_STR}/openapi.json",
    lifespan=lifespan
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
