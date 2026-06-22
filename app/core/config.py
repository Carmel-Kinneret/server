from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Carmel Kinneret Server"
    API_V1_STR: str = "/api"
    
    # Database
    # Database URL is read from .env (DATABASE_URL). Fallback to local SQLite for dev.
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    
    # Clerk Authentication
    CLERK_ISSUER: str = ""
    CLERK_FRONTEND_API: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")

settings = Settings()
