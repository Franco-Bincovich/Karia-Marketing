"""Biblioteca de imágenes — upload manual + OpenAI key."""

import logging
from uuid import UUID

import requests
from sqlalchemy.orm import Session

from config.settings import get_settings
from middleware.error_handler import AppError
from repositories import imagenes_repository as repo
from services.imagen.storage import _BUCKET, _build_storage_url
from utils.security import encrypt_token

logger = logging.getLogger(__name__)

ALLOWED_IMAGE_TYPES = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
MAX_IMAGE_SIZE = 20 * 1024 * 1024  # 20MB

CONTENT_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".gif": "image/gif",
}


def biblioteca_subir(db: Session, marca_id: UUID, filename: str, content: bytes) -> dict:
    """Sube imagen manual a Supabase Storage y guarda en DB."""
    ext = ("." + filename.rsplit(".", 1)[-1].lower()) if "." in filename else ""

    if ext not in ALLOWED_IMAGE_TYPES:
        raise AppError(f"Formato no soportado: {ext}. Usar JPG, PNG, WEBP o GIF.", "INVALID_FILE_TYPE", 400)
    if len(content) > MAX_IMAGE_SIZE:
        raise AppError("El archivo excede el límite de 20MB.", "FILE_TOO_LARGE", 400)

    settings = get_settings()
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
        raise AppError("Supabase Storage no configurado.", "IMAGE_STORAGE_ERROR", 500)

    import uuid as uuid_mod

    safe_name = f"{uuid_mod.uuid4().hex}{ext}"
    path = f"{marca_id}/biblioteca/{safe_name}"
    storage_url = _build_storage_url(settings.SUPABASE_URL, _BUCKET, path)

    resp = requests.post(
        storage_url,
        headers={
            "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
            "Content-Type": CONTENT_TYPES.get(ext, "application/octet-stream"),
        },
        data=content,
        timeout=30,
    )

    if resp.status_code not in (200, 201):
        logger.error("[biblioteca] upload failed %s — %s", resp.status_code, resp.text[:200])
        raise AppError(f"Error al subir imagen (HTTP {resp.status_code})", "IMAGE_STORAGE_ERROR", 500)

    public_url = storage_url.replace("/object/", "/object/public/")

    img = repo.crear(
        db,
        {
            "marca_id": marca_id,
            "prompt": filename,
            "imagen_url": public_url,
            "tamano": "original",
            "estilo": "manual",
            "origen": "manual",
        },
    )
    db.commit()
    logger.info("[biblioteca] subido %s", filename)
    return img


def biblioteca_listar(db: Session, marca_id: UUID) -> list[dict]:
    return repo.listar_por_origen(db, marca_id, "manual")


def biblioteca_eliminar(db: Session, marca_id: UUID, imagen_id: UUID) -> bool:
    obj = repo.eliminar(db, imagen_id, marca_id)
    if not obj:
        raise AppError("Imagen no encontrada", "NOT_FOUND", 404)
    if obj.imagen_url:
        settings = get_settings()
        if settings.SUPABASE_SERVICE_KEY:
            del_url = obj.imagen_url.replace("/object/public/", "/object/")
            try:
                requests.delete(del_url, headers={"Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}"}, timeout=10)
            except Exception:
                logger.warning("[biblioteca] Error eliminando de storage")
    db.commit()
    return True


def guardar_openai_key(db: Session, cliente_id: UUID, api_key: str, plan: str) -> dict:
    """Guarda API key propia de OpenAI encriptada."""
    from models.cliente_models import ClienteMkt

    if plan not in ("Premium",):
        raise AppError("Solo Premium puede usar API key propia", "PLAN_LIMIT", 403)
    cliente = db.query(ClienteMkt).filter(ClienteMkt.id == cliente_id).first()
    if not cliente:
        raise AppError("Cliente no encontrado", "CLIENT_NOT_FOUND", 404)
    cliente.openai_api_key_encrypted = encrypt_token(api_key)
    db.commit()
    return {"message": "OpenAI API key guardada", "has_custom_key": True}
