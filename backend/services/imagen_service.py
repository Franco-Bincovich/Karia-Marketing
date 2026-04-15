"""Servicio de generación de imágenes con IA — Módulo 6."""

import base64
import logging
from typing import Optional
from uuid import UUID

import requests
from sqlalchemy.orm import Session

from config.settings import get_settings
from integrations.openai_client import (
    OpenAIError,
    generar_imagen,
    generar_imagen_desde_marca,
)
from middleware.error_handler import AppError
from repositories import contenido_repository as contenido_repo
from repositories import imagenes_repository as repo
from repositories import memoria_marca_repository as memoria_repo
from utils.security import decrypt_token, encrypt_token

logger = logging.getLogger(__name__)


def _get_context(db: Session, marca_id: UUID):
    """Obtiene cliente y perfil de marca."""
    from models.cliente_models import ClienteMkt, MarcaMkt
    marca = db.query(MarcaMkt).filter(MarcaMkt.id == marca_id).first()
    if not marca:
        raise AppError("Marca no encontrada", "MARCA_NOT_FOUND", 404)
    cliente = db.query(ClienteMkt).filter(ClienteMkt.id == marca.cliente_id).first()
    if not cliente:
        raise AppError("Cliente no encontrado", "CLIENT_NOT_FOUND", 404)
    return cliente, marca


def _custom_openai_key(cliente, rol: str = "") -> Optional[str]:
    """Devuelve API key propia si existe y tiene permiso."""
    if cliente.openai_api_key_encrypted and (cliente.plan == "Premium" or rol == "superadmin"):
        return decrypt_token(cliente.openai_api_key_encrypted)
    return None


def _upload_to_supabase(b64_data: str, marca_id: UUID, filename: str) -> str:
    """Sube imagen a Supabase Storage y retorna URL pública."""
    settings = get_settings()
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
        logger.warning("[imagen_svc] Supabase Storage no configurado — usando URL placeholder")
        return f"https://placeholder.nexo.ai/imagenes/{marca_id}/{filename}"

    bucket = "imagenes-nexo"
    path = f"{marca_id}/{filename}"
    image_bytes = base64.b64decode(b64_data)

    # Use REST API to upload
    base_url = settings.SUPABASE_URL.rstrip("/")
    # Extract the project ref from the dashboard URL or construct storage URL
    if "supabase.com/dashboard" in base_url:
        # Dashboard URL format: https://supabase.com/dashboard/project/{ref}
        ref = base_url.split("/")[-1]
        storage_url = f"https://{ref}.supabase.co/storage/v1/object/{bucket}/{path}"
    else:
        storage_url = f"{base_url}/storage/v1/object/{bucket}/{path}"

    resp = requests.post(
        storage_url,
        headers={
            "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
            "Content-Type": "image/png",
        },
        data=image_bytes,
        timeout=30,
    )

    if resp.status_code in (200, 201):
        public_url = storage_url.replace("/object/", "/object/public/")
        logger.info(f"[imagen_svc] uploaded — {path}")
        return public_url

    logger.warning(f"[imagen_svc] upload failed {resp.status_code} — using b64 fallback")
    return f"data:image/png;base64,{b64_data[:100]}..."


def generar(
    db: Session,
    marca_id: UUID,
    descripcion: str,
    tamano: str = "1024x1024",
    estilo: str = "vivid",
    usar_perfil: bool = True,
    rol: str = "",
) -> dict:
    """Genera imagen desde descripción libre, opcionalmente enriquecida con perfil de marca."""
    cliente, marca = _get_context(db, marca_id)
    custom_key = _custom_openai_key(cliente, rol)

    try:
        if usar_perfil:
            perfil = memoria_repo.obtener_o_crear(db, marca_id)
            result = generar_imagen_desde_marca(
                descripcion, perfil, size=tamano, style=estilo, custom_api_key=custom_key,
            )
        else:
            result = generar_imagen(
                descripcion, size=tamano, style=estilo, custom_api_key=custom_key,
            )
    except OpenAIError as e:
        raise AppError(f"Error al generar imagen: {e.message}", "OPENAI_ERROR", e.status_code)

    import uuid as uuid_mod
    filename = f"{uuid_mod.uuid4().hex}.png"

    if result.get("b64_data"):
        imagen_url = _upload_to_supabase(result["b64_data"], marca_id, filename)
    else:
        imagen_url = result.get("url", "")

    img = repo.crear(db, {
        "marca_id": marca_id,
        "prompt": result.get("revised_prompt") or descripcion,
        "imagen_url": imagen_url,
        "tamano": tamano,
        "estilo": estilo,
    })
    db.commit()
    return img


def generar_para_contenido(
    db: Session,
    marca_id: UUID,
    contenido_id: UUID,
    tamano: str = "1024x1024",
    estilo: str = "vivid",
    rol: str = "",
) -> dict:
    """Genera imagen para un contenido existente usando el copy como contexto."""
    cliente, marca = _get_context(db, marca_id)
    custom_key = _custom_openai_key(cliente, rol)

    obj = contenido_repo.obtener(db, contenido_id, marca_id)
    if not obj:
        raise AppError("Contenido no encontrado", "NOT_FOUND", 404)

    variante = obj.variante_seleccionada or "a"
    copy_text = getattr(obj, f"copy_{variante}") or obj.copy_a or ""
    descripcion = f"Imagen para post de {obj.red_social}: {copy_text[:300]}"

    perfil = memoria_repo.obtener_o_crear(db, marca_id)

    try:
        result = generar_imagen_desde_marca(
            descripcion, perfil, size=tamano, style=estilo, custom_api_key=custom_key,
        )
    except OpenAIError as e:
        raise AppError(f"Error al generar imagen: {e.message}", "OPENAI_ERROR", e.status_code)

    import uuid as uuid_mod
    filename = f"{uuid_mod.uuid4().hex}.png"

    if result.get("b64_data"):
        imagen_url = _upload_to_supabase(result["b64_data"], marca_id, filename)
    else:
        imagen_url = result.get("url", "")

    img = repo.crear(db, {
        "marca_id": marca_id,
        "contenido_id": contenido_id,
        "prompt": result.get("revised_prompt") or descripcion,
        "imagen_url": imagen_url,
        "tamano": tamano,
        "estilo": estilo,
    })

    contenido_repo.actualizar_campos(db, obj, {"imagen_url": imagen_url})
    db.commit()
    return img


def asociar_contenido(
    db: Session,
    marca_id: UUID,
    imagen_id: UUID,
    contenido_id: UUID,
) -> dict:
    """Asocia una imagen existente a un contenido."""
    img = repo.obtener(db, imagen_id, marca_id)
    if not img:
        raise AppError("Imagen no encontrada", "NOT_FOUND", 404)

    obj_contenido = contenido_repo.obtener(db, contenido_id, marca_id)
    if not obj_contenido:
        raise AppError("Contenido no encontrado", "NOT_FOUND", 404)

    img.contenido_id = contenido_id
    contenido_repo.actualizar_campos(db, obj_contenido, {"imagen_url": img.imagen_url})
    db.flush()
    db.commit()

    return {
        "imagen_id": str(imagen_id),
        "contenido_id": str(contenido_id),
        "imagen_url": img.imagen_url,
    }


def listar(db: Session, marca_id: UUID) -> list[dict]:
    return repo.listar(db, marca_id)


def guardar_openai_key(db: Session, cliente_id: UUID, api_key: str, plan: str) -> dict:
    """Guarda API key propia de OpenAI encriptada."""
    from models.cliente_models import ClienteMkt
    if plan not in ("Premium",) :
        raise AppError("Solo Premium puede usar API key propia", "PLAN_LIMIT", 403)
    cliente = db.query(ClienteMkt).filter(ClienteMkt.id == cliente_id).first()
    if not cliente:
        raise AppError("Cliente no encontrado", "CLIENT_NOT_FOUND", 404)
    cliente.openai_api_key_encrypted = encrypt_token(api_key)
    db.commit()
    return {"message": "OpenAI API key guardada", "has_custom_key": True}
