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
        raise AppError(
            "Supabase Storage no configurado. Verificá SUPABASE_URL y SUPABASE_SERVICE_KEY.",
            "IMAGE_STORAGE_ERROR", 500,
        )

    bucket = "Nexo - Marketing - Imagens"
    path = f"{marca_id}/{filename}"
    image_bytes = base64.b64decode(b64_data)

    base_url = settings.SUPABASE_URL.rstrip("/")
    if "supabase.com/dashboard" in base_url:
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
        logger.info("[imagen_svc] uploaded — %s", path)
        return public_url

    logger.error("[imagen_svc] upload failed %s — %s", resp.status_code, resp.text[:200])
    raise AppError(
        f"Error al subir imagen a Supabase Storage (HTTP {resp.status_code})",
        "IMAGE_STORAGE_ERROR", 500,
    )


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


FORMAT_SIZE_MAP = {
    "post": "1024x1024",
    "carrusel": "1024x1024",
    "reel": "1024x1792",
    "story": "1024x1792",
}


def _size_for_format(formato: str, tamano_override: Optional[str] = None) -> str:
    """Retorna el tamaño de imagen adecuado según formato, o el override si se provee."""
    if tamano_override and tamano_override != "auto":
        return tamano_override
    return FORMAT_SIZE_MAP.get(formato, "1024x1024")


def generar_para_contenido(
    db: Session,
    marca_id: UUID,
    contenido_id: UUID,
    tamano: str = "auto",
    estilo: str = "vivid",
    rol: str = "",
) -> dict:
    """Genera imagen para un contenido existente. Tamaño auto según formato."""
    cliente, marca = _get_context(db, marca_id)
    custom_key = _custom_openai_key(cliente, rol)

    obj = contenido_repo.obtener(db, contenido_id, marca_id)
    if not obj:
        raise AppError("Contenido no encontrado", "NOT_FOUND", 404)

    size = _size_for_format(obj.formato, tamano if tamano != "auto" else None)
    variante = obj.variante_seleccionada or "a"
    copy_text = getattr(obj, f"copy_{variante}") or obj.copy_a or ""
    descripcion = f"Imagen para {obj.formato} de {obj.red_social}: {copy_text[:300]}"

    perfil = memoria_repo.obtener_o_crear(db, marca_id)

    try:
        result = generar_imagen_desde_marca(
            descripcion, perfil, size=size, style=estilo, custom_api_key=custom_key,
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
        "tamano": size,
        "estilo": estilo,
    })

    contenido_repo.actualizar_campos(db, obj, {"imagen_url": imagen_url})
    db.commit()
    return img


def generar_carrusel(
    db: Session,
    marca_id: UUID,
    contenido_id: UUID,
    num_slides: int = 5,
    estilo: str = "vivid",
    rol: str = "",
) -> dict:
    """Genera N slides para un carrusel: copies + imágenes por slide."""
    cliente, marca = _get_context(db, marca_id)
    custom_key = _custom_openai_key(cliente, rol)

    obj = contenido_repo.obtener(db, contenido_id, marca_id)
    if not obj:
        raise AppError("Contenido no encontrado", "NOT_FOUND", 404)

    num_slides = max(2, min(10, num_slides))
    variante = obj.variante_seleccionada or "a"
    copy_text = getattr(obj, f"copy_{variante}") or obj.copy_a or ""
    perfil = memoria_repo.obtener_o_crear(db, marca_id)

    # Generate slide copies with Claude
    from integrations.claude_client import _get_client, _SEARCH_MODEL, _parse_json_object
    import json

    client = _get_client()
    message = client.messages.create(
        model=_SEARCH_MODEL,
        max_tokens=2048,
        system=(
            f"Sos un experto en carruseles de Instagram. "
            f"Perfil de marca: {memoria_repo.obtener_para_agente(db, marca_id)}"
        ),
        messages=[{"role": "user", "content": (
            f"Creá un carrusel de {num_slides} slides para Instagram basado en este copy:\n\n"
            f"{copy_text}\n\n"
            f"Para cada slide incluí:\n"
            f"- copy_slide: texto breve para el slide (max 100 chars)\n"
            f"- descripcion_imagen: prompt para generar la imagen del slide\n\n"
            f'Respondé con JSON: {{"slides": [{{"copy_slide": "...", "descripcion_imagen": "..."}}]}}'
        )}],
    )

    text_blocks = [b for b in message.content if b.type == "text"]
    try:
        data = _parse_json_object(text_blocks[-1].text)
        slides_data = data.get("slides", [])[:num_slides]
    except Exception:
        slides_data = [{"copy_slide": f"Slide {i+1}", "descripcion_imagen": copy_text[:200]} for i in range(num_slides)]

    # Generate images and create slide records
    from models.contenido_models import CarruselSlideMkt
    slides_result = []

    for i, slide in enumerate(slides_data):
        try:
            result = generar_imagen_desde_marca(
                slide.get("descripcion_imagen", f"Slide {i+1} de carrusel"),
                perfil, size="1024x1024", style=estilo, custom_api_key=custom_key,
            )
            import uuid as uuid_mod
            filename = f"{uuid_mod.uuid4().hex}.png"
            if result.get("b64_data"):
                img_url = _upload_to_supabase(result["b64_data"], marca_id, filename)
            else:
                img_url = result.get("url", "")
        except Exception as e:
            logger.warning("Error generando slide %d: %s", i+1, e)
            img_url = ""

        slide_obj = CarruselSlideMkt(
            contenido_id=contenido_id,
            orden=i + 1,
            imagen_url=img_url,
            copy_slide=slide.get("copy_slide", f"Slide {i+1}"),
        )
        db.add(slide_obj)
        db.flush()
        slides_result.append({
            "id": str(slide_obj.id), "orden": slide_obj.orden,
            "imagen_url": slide_obj.imagen_url, "copy_slide": slide_obj.copy_slide,
        })

    # Set first slide as contenido imagen_url
    if slides_result and slides_result[0].get("imagen_url"):
        contenido_repo.actualizar_campos(db, obj, {"imagen_url": slides_result[0]["imagen_url"]})

    db.commit()
    return {"contenido_id": str(contenido_id), "num_slides": len(slides_result), "slides": slides_result}


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
