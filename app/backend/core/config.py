"""Application configuration."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    DATABASE_URL: str = "postgresql://totalmanager:totalmanager123@localhost:5432/totalmanager"
    SECRET_KEY: str = "dev-secret-key-change-in-production-please-use-strong-random-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

