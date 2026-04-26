"""Configuración central de la aplicación via variables de entorno."""

from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str  # Required — sin default. Debe tener >= 32 chars.
    JWT_EXPIRATION_HOURS: int = 24
    SECRET_KEY: str  # Required — sin default. Debe tener >= 32 chars.
    ENV: str = "development"  # "development" | "production"
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

    @field_validator("JWT_SECRET", "SECRET_KEY")
    @classmethod
    def _validate_secrets(cls, v: str, info) -> str:
        if not v or len(v) < 32:
            raise ValueError(f"{info.field_name} debe tener al menos 32 caracteres. Generá uno con: openssl rand -hex 64")
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """Retorna instancia cacheada de Settings."""
    return Settings()
