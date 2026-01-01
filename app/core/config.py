from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from functools import lru_cache

class Settings(BaseSettings):
    """Application setting for Language Learning App."""

    # Application
    APP_NAME: str = "Language app"
    DESCRIPTION: str = "API for learning English and German with AI-generated exercises"
    VERSION: str = "0.1.0"
    DEBUG: bool = True
    ENVIRONMENT: Literal["development", "production"] = "development"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    #CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    ALLOWED_HOSTS: list[str] = []

    # Data base PostrgreSQL
    POSTGRES_USER: str = Field(..., description="PostgreSQL username")
    POSTGRES_PASSWORD: str = Field(..., description="Database password")
    POSTGRES_HOST: str = Field(default="localhost")
    POSTGRES_PORT: int = Field(default=5432)
    POSTGRES_DB: str = Field(..., description="PostgreSQL database name")

    # Security
    SECRET_KEY: str = Field(..., min_length=32, description="JWT secret key")
    JWT_ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # Logging
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    LOG_FORMAT: str = "[{time:YYYY-MM-DD HH:mm:ss}] | {level:<8} | {extra[log_id]} | user={extra[user_id]} | {message}"
    LOG_FILE: str = "logs/app.log"

    # Configuration pydantic-settings
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='ignore',
    )

    # Validation
    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("SECRET KEY must be at least 32 characters")
        return v

    @field_validator("PORT")
    @classmethod
    def validate_port(cls, v: int) -> int:
        if not 1024 <= v <= 65535:
            raise ValueError("PORT must be between 1024 and 65535")
        return v

    # Data base URL
    @property
    def database_url(self) -> str:
        """Formating a URL to connect to PostgreSQL."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def sync_database_url(self) -> str:
        """Sync URL for Alembic migration."""
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # Computed properties
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.ENVIRONMENT == "production"

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings"""
    return Settings()

settings = get_settings()