"""Lógica de Supabase Storage para imágenes."""

import base64
import logging
from uuid import UUID

import requests

from config.settings import get_settings
from middleware.error_handler import AppError

logger = logging.getLogger(__name__)

_BUCKET = "Nexo - Marketing - Imagens"


def _build_storage_url(base_url: str, bucket: str, path: str) -> str:
    """Construye la URL de storage según el formato de SUPABASE_URL."""
    base = base_url.rstrip("/")
    if "supabase.com/dashboard" in base:
        ref = base.split("/")[-1]
        return f"https://{ref}.supabase.co/storage/v1/object/{bucket}/{path}"
    return f"{base}/storage/v1/object/{bucket}/{path}"


def upload_to_supabase(b64_data: str, marca_id: UUID, filename: str) -> str:
    """Sube imagen (base64) a Supabase Storage y retorna URL pública."""
    settings = get_settings()
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
        raise AppError("Supabase Storage no configurado.", "IMAGE_STORAGE_ERROR", 500)

    path = f"{marca_id}/{filename}"
    image_bytes = base64.b64decode(b64_data)
    storage_url = _build_storage_url(settings.SUPABASE_URL, _BUCKET, path)

    resp = requests.post(
        storage_url,
        headers={"Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}", "Content-Type": "image/png"},
        data=image_bytes,
        timeout=30,
    )

    if resp.status_code in (200, 201):
        logger.info("[imagen_storage] uploaded — %s", path)
        return storage_url.replace("/object/", "/object/public/")

    logger.error("[imagen_storage] upload failed %s — %s", resp.status_code, resp.text[:200])
    raise AppError(f"Error al subir imagen (HTTP {resp.status_code})", "IMAGE_STORAGE_ERROR", 500)
