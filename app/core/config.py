from pydantic_settings import BaseSettings
from typing import List, Optional



class Settings(BaseSettings):
    # Project settings
    PROJECT_NAME: str = "FastAPI Production App"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    _BASE_URL: str = f"https://{HOST}:{PORT}"
    # quantity of workers for uvicorn
    WORKERS_COUNT: int = 1
    # Enable uvicorn reloading
    RELOAD: bool = False

    # Database settings
    DB_NAME: str = "prometheus-metrics-db"
    DB_USER: str = "postgres"
    DB_PASS: str = "postgres"
    DB_HOST: str = "postgres"
    DB_PORT: int = 5432
    DATABASE_URL: str ="postgresql+asyncpg://postgres:postgres@localhost:5432/prometheus-metrics-db"

    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # Security settings
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    # CORS settings
    ALLOWED_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Redis settings (for caching/sessions)
    REDIS_URL: Optional[str] = None

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
