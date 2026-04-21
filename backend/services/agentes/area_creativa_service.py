"""Área Creativa — orquesta Director de Arte + Agente Visual + Copy Visual."""

import base64
import logging
import uuid as uuid_mod
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from middleware.error_handler import AppError
from repositories import imagenes_repository as repo
from repositories import memoria_marca_repository as memoria_repo

logger = logging.getLogger(__name__)

# Tamaños por formato (px reales)
TAMANOS = {
    "post": (1080, 1080),
    "carrusel": (1080, 1080),
    "historia": (1080, 1920),
    "reel": (1080, 1920),
    "facebook_post": (1200, 630),
}


def generar_pieza(
    db: Session,
    marca_id: UUID,
    descripcion: str,
    formato: str = "post",
    rol: str = "",
) -> dict:
    """
    Punto de entrada único para generación de imágenes del Área Creativa.

    Flujo: Director de Arte → Agente Visual → Copy Visual (si placa)
    """
    from services.agentes import director_arte_service as director
    from services.agentes import agente_visual_service as visual
    from services.agentes import agente_copy_visual_service as copy_visual

    perfil = memoria_repo.obtener_o_crear(db, marca_id)
    leo_key = _resolve_leo_key(db, marca_id)
    w, h = TAMANOS.get(formato, (1080, 1080))

    # 1. Director de Arte analiza el brief
    logger.info("[area_creativa] iniciando — formato=%s, desc=%s", formato, descripcion[:60])
    brief = director.analizar_brief(descripcion, perfil, formato)
    tipo = brief.get("tipo", "elaborada")
    logger.info("[area_creativa] brief → tipo=%s", tipo)

    # 2. Agente Visual genera la imagen
    try:
        result = visual.generar(brief, perfil, leo_key=leo_key)
    except Exception as e:
        logger.error("[area_creativa] visual falló: %s", e)
        raise AppError(f"Error al generar imagen: {e}", "IMAGE_GEN_ERROR", 500)

    imagen_url = result.get("url", "")

    # 3. Si es placa, Copy Visual aplica texto
    if tipo == "placa" and imagen_url and brief.get("texto_principal"):
        try:
            png_bytes = copy_visual.aplicar_texto(
                imagen_url, brief, perfil, w, h,
            )
            filename = f"{uuid_mod.uuid4().hex}.png"
            b64_data = base64.b64encode(png_bytes).decode()
            imagen_url = _upload_to_supabase(b64_data, marca_id, filename)
        except Exception as e:
            logger.warning("[area_creativa] copy_visual falló, usando imagen sin texto: %s", e)

    # Si no es placa pero tiene b64_data (OpenAI fallback), subir
    elif result.get("b64_data"):
        filename = f"{uuid_mod.uuid4().hex}.png"
        imagen_url = _upload_to_supabase(result["b64_data"], marca_id, filename)

    # 4. Guardar en DB
    img = repo.crear(db, {
        "marca_id": marca_id,
        "prompt": result.get("revised_prompt") or descripcion,
        "imagen_url": imagen_url,
        "tamano": f"{w}x{h}",
        "estilo": tipo,
        "origen": "ia",
    })
    db.commit()
    logger.info("[area_creativa] pieza generada — tipo=%s, url=%s", tipo, imagen_url[:60] if imagen_url else "?")
    return img


def _resolve_leo_key(db: Session, marca_id: UUID) -> Optional[str]:
    """Reutiliza la resolución de key de imagen_service."""
    from services.imagen_service import _resolve_leonardo_key, _get_context
    cliente, _ = _get_context(db, marca_id)
    return _resolve_leonardo_key(db, cliente.id)


def _upload_to_supabase(b64_data: str, marca_id: UUID, filename: str) -> str:
    """Reutiliza el upload de imagen_service."""
    from services.imagen_service import _upload_to_supabase
    return _upload_to_supabase(b64_data, marca_id, filename)
