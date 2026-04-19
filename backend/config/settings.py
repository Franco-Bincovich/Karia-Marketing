"""Configuración central de la aplicación via variables de entorno."""

from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str = "change-me-in-production"
    JWT_EXPIRATION_HOURS: int = 24
    SECRET_KEY: str = "change-me-in-production"
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    KARIA_API_KEY: str = ""
    ENCRYPTION_KEY: str = ""
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:1706",
        "http://localhost:3002",
    ]
    PORT: int = 3002
    NODE_ENV: str = "development"
    ALLOWED_ORIGINS: str = "http://localhost:5173"
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_KEY: str = ""
    ZERNIO_API_KEY: str = ""
    ZERNIO_BASE_URL: str = "https://api.zernio.com/v1"
    SEMRUSH_API_KEY: str = ""
    MENTION_API_KEY: str = ""
    MANYCHAT_API_KEY: str = ""
    LEONARDO_API_KEY: str = ""
    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = "Nexo <noreply@nexo.marketing>"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """Retorna instancia cacheada de Settings."""
    return Settings()
