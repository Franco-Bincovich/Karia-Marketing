"""Helpers internos del módulo de imágenes — keys, contexto, constantes."""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from config.settings import get_settings
from middleware.error_handler import AppError
from utils.security import decrypt_token

logger = logging.getLogger(__name__)

TAMANOS = {
    "post": (1080, 1080),
    "carrusel": (1080, 1080),
    "historia": (1080, 1920),
    "reel": (1080, 1920),
    "facebook_post": (1200, 630),
}

_FORMATO_LEO_SIZE = {
    "post": "1024x1024",
    "carrusel": "1024x1024",
    "historia": "1024x1792",
    "reel": "1024x1792",
    "facebook_post": "1792x1024",
}


def resolve_leonardo_key(db: Session, cliente_id: UUID) -> Optional[str]:
    """Busca Leonardo API key en .env o en la DB."""
    env_key = get_settings().LEONARDO_API_KEY
    if env_key:
        return env_key
    from repositories.api_keys_repository import obtener_leonardo_key

    return obtener_leonardo_key(db, cliente_id)


def get_context(db: Session, marca_id: UUID) -> tuple:
    """Obtiene cliente y marca. Lanza AppError si no existen."""
    from models.cliente_models import ClienteMkt, MarcaMkt

    marca = db.query(MarcaMkt).filter(MarcaMkt.id == marca_id).first()
    if not marca:
        raise AppError("Marca no encontrada", "MARCA_NOT_FOUND", 404)
    cliente = db.query(ClienteMkt).filter(ClienteMkt.id == marca.cliente_id).first()
    if not cliente:
        raise AppError("Cliente no encontrado", "CLIENT_NOT_FOUND", 404)
    return cliente, marca


def custom_openai_key(cliente, rol: str = "") -> Optional[str]:
    """Devuelve API key propia si existe y tiene permiso."""
    if cliente.openai_api_key_encrypted and (cliente.plan == "Premium" or rol == "superadmin"):
        return decrypt_token(cliente.openai_api_key_encrypted)
    return None


def gen_imagen(db: Session, cliente_id: UUID, prompt: str, size: str, style: str, openai_key=None, tipo: str = "elaborada") -> dict:
    """Genera imagen con Leonardo (preferido) o OpenAI (fallback)."""
    leo_key = resolve_leonardo_key(db, cliente_id)
    if leo_key:
        from integrations.leonardo_client import LeonardoError, generar_imagen

        try:
            return generar_imagen(prompt, size=size, style=style, custom_api_key=leo_key, tipo=tipo)
        except LeonardoError as e:
            raise AppError(f"Error al generar imagen: {e.message}", "IMAGE_GEN_ERROR", e.status_code)

    if get_settings().OPENAI_API_KEY or openai_key:
        from integrations.openai_client import generar_imagen

        return generar_imagen(prompt, size=size, style=style, custom_api_key=openai_key)

    raise AppError("No hay proveedor de imágenes configurado.", "NO_IMAGE_PROVIDER", 400)


def gen_imagen_marca(db, cliente_id, descripcion, perfil, size, style, openai_key=None, tipo="elaborada") -> dict:
    """Genera imagen con perfil de marca — Leonardo o OpenAI."""
    leo_key = resolve_leonardo_key(db, cliente_id)
    if leo_key:
        from integrations.leonardo_client import LeonardoError, generar_imagen_desde_marca

        try:
            return generar_imagen_desde_marca(descripcion, perfil, size=size, style=style, custom_api_key=leo_key, tipo=tipo)
        except LeonardoError as e:
            raise AppError(f"Error al generar imagen: {e.message}", "IMAGE_GEN_ERROR", e.status_code)

    if get_settings().OPENAI_API_KEY or openai_key:
        from integrations.openai_client import generar_imagen_desde_marca

        return generar_imagen_desde_marca(descripcion, perfil, size=size, style=style, custom_api_key=openai_key)

    raise AppError("No hay proveedor de imágenes configurado.", "NO_IMAGE_PROVIDER", 400)


def size_for_format(formato: str, tamano_override: Optional[str] = None) -> str:
    """Retorna size key de Leonardo según formato."""
    if tamano_override and tamano_override != "auto":
        return tamano_override
    return _FORMATO_LEO_SIZE.get(formato, "1024x1024")


def pixels_for_format(formato: Optional[str]) -> tuple:
    """Retorna (width, height) en px según formato."""
    if formato and formato in TAMANOS:
        return TAMANOS[formato]
    return (1080, 1080)
