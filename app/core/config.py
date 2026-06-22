import base64
from pydantic_settings import BaseSettings, SettingsConfigDict

def get_clerk_domain(publishable_key: str) -> str:
    if not publishable_key:
        return ""
    try:
        parts = publishable_key.split("_")
        if len(parts) >= 3:
            encoded_part = parts[2]
            padding = len(encoded_part) % 4
            if padding:
                encoded_part += "=" * (4 - padding)
            decoded = base64.b64decode(encoded_part).decode("utf-8")
            if decoded.endswith("$"):
                decoded = decoded[:-1]
            return f"https://{decoded}"
    except Exception:
        pass
    return ""

def get_supabase_project_ref(supabase_url: str) -> str:
    if not supabase_url:
        return ""
    try:
        host = supabase_url.split("//")[-1]
        project_ref = host.split(".")[0]
        return project_ref
    except Exception:
        pass
    return ""

class Settings(BaseSettings):
    PROJECT_NAME: str = "Carmel Kinneret Server"
    API_V1_STR: str = "/api"
    
    # Database
    # Database URL is read from .env (DATABASE_URL). Fallback to local SQLite for dev.
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    
    # Clerk Authentication
    CLERK_ISSUER: str = ""
    CLERK_FRONTEND_API: str = ""
    CLERK_PUBLISHABLE_KEY: str = ""
    CLERK_SECRET_KEY: str = ""
    
    # Supabase Configuration
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_DB_PASSWORD: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")

    def model_post_init(self, __context):
        # Auto-derive Clerk issuer and frontend api from publishable key
        if self.CLERK_PUBLISHABLE_KEY and (not self.CLERK_ISSUER or not self.CLERK_FRONTEND_API):
            derived_clerk = get_clerk_domain(self.CLERK_PUBLISHABLE_KEY)
            if derived_clerk:
                if not self.CLERK_ISSUER:
                    self.CLERK_ISSUER = derived_clerk
                if not self.CLERK_FRONTEND_API:
                    self.CLERK_FRONTEND_API = derived_clerk
        
        # Auto-derive DATABASE_URL from Supabase parameters if DATABASE_URL is default/empty
        if (self.DATABASE_URL == "sqlite+aiosqlite:///./test.db" or not self.DATABASE_URL) and self.SUPABASE_URL and self.SUPABASE_DB_PASSWORD:
            project_ref = get_supabase_project_ref(self.SUPABASE_URL)
            if project_ref:
                self.DATABASE_URL = f"postgresql+asyncpg://postgres:{self.SUPABASE_DB_PASSWORD}@db.{project_ref}.supabase.co:5432/postgres"

settings = Settings()

