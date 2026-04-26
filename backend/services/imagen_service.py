"""Servicio de generación de imágenes con IA — orquestador principal."""

import logging
import uuid as uuid_mod
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from middleware.error_handler import AppError
from repositories import contenido_repository as contenido_repo
from repositories import imagenes_repository as repo
from repositories import memoria_marca_repository as memoria_repo

# Re-exports para backward compat (callers existentes importan de acá)
from services.imagen.biblioteca import (  # noqa: F401
    biblioteca_eliminar,
    biblioteca_listar,
    biblioteca_subir,
    guardar_openai_key,
)
from services.imagen.helpers import (  # noqa: F401
    _FORMATO_LEO_SIZE,
    TAMANOS,
)
from services.imagen.helpers import (
    custom_openai_key as _custom_openai_key,
)
from services.imagen.helpers import (
    gen_imagen as _gen_imagen,
)
from services.imagen.helpers import (
    gen_imagen_marca as _gen_imagen_marca,
)
from services.imagen.helpers import (
    get_context as _get_context,
)
from services.imagen.helpers import (
    resolve_leonardo_key as _resolve_leonardo_key,
)
from services.imagen.helpers import (
    size_for_format as _size_for_format,
)
from services.imagen.storage import upload_to_supabase as _upload_to_supabase

logger = logging.getLogger(__name__)


def generar(
    db: Session,
    marca_id: UUID,
    descripcion: str,
    tamano: str = "1024x1024",
    estilo: str = "vivid",
    usar_perfil: bool = True,
    rol: str = "",
    tipo: str = "elaborada",
    formato: Optional[str] = None,
) -> dict:
    """Genera imagen, opcionalmente enriquecida con perfil de marca."""
    import base64 as b64_mod

    cliente, marca = _get_context(db, marca_id)

    if formato and formato in TAMANOS:
        w, h = TAMANOS[formato]
        leo_size = _FORMATO_LEO_SIZE.get(formato, "1024x1024")
    else:
        w, h = (1080, 1080)
        leo_size = tamano

    # Placa con texto
    if tipo == "placa":
        import re

        from integrations.placa_client import generar_placa

        perfil = memoria_repo.obtener_o_crear(db, marca_id)
        colores_str = " ".join(perfil.get("colores_marca", []) if isinstance(perfil.get("colores_marca"), list) else [])
        hex_codes = re.findall(r"#[0-9A-Fa-f]{6}", colores_str)
        leo_key = _resolve_leonardo_key(db, cliente.id)
        png_bytes = generar_placa(descripcion, colores_hex=hex_codes, width=w, height=h, leonardo_api_key=leo_key, size_key=leo_size)
        b64_data = b64_mod.b64encode(png_bytes).decode()
        imagen_url = _upload_to_supabase(b64_data, marca_id, f"{uuid_mod.uuid4().hex}.png")
        img = repo.crear(
            db, {"marca_id": marca_id, "prompt": descripcion, "imagen_url": imagen_url, "tamano": f"{w}x{h}", "estilo": "placa", "origen": "ia"}
        )
        db.commit()
        return img

    # Área Creativa (Director de Arte + Visual + Copy)
    if usar_perfil:
        try:
            from services.agentes.area_creativa_service import generar_pieza

            return generar_pieza(db, marca_id, descripcion, formato=formato or "post", rol=rol)
        except Exception as e:
            logger.warning("[imagen_svc] area_creativa falló, fallback: %s", e)

    # Fallback directo
    openai_key = _custom_openai_key(cliente, rol)
    result = _gen_imagen(db, cliente.id, descripcion, size=leo_size, style=estilo, openai_key=openai_key)
    filename = f"{uuid_mod.uuid4().hex}.png"
    imagen_url = _upload_to_supabase(result["b64_data"], marca_id, filename) if result.get("b64_data") else result.get("url", "")
    img = repo.crear(
        db,
        {
            "marca_id": marca_id,
            "prompt": result.get("revised_prompt") or descripcion,
            "imagen_url": imagen_url,
            "tamano": f"{w}x{h}",
            "estilo": estilo,
        },
    )
    db.commit()
    return img


def generar_para_contenido(db: Session, marca_id: UUID, contenido_id: UUID, tamano: str = "auto", estilo: str = "vivid", rol: str = "") -> dict:
    """Genera imagen para un contenido existente."""
    cliente, marca = _get_context(db, marca_id)
    obj = contenido_repo.obtener(db, contenido_id, marca_id)
    if not obj:
        raise AppError("Contenido no encontrado", "NOT_FOUND", 404)
    size = _size_for_format(obj.formato, tamano if tamano != "auto" else None)
    variante = obj.variante_seleccionada or "a"
    copy_text = getattr(obj, f"copy_{variante}") or obj.copy_a or ""
    perfil = memoria_repo.obtener_o_crear(db, marca_id)
    result = _gen_imagen_marca(
        db, cliente.id, f"Imagen para {obj.formato}: {copy_text[:300]}", perfil, size=size, style=estilo, openai_key=_custom_openai_key(cliente, rol)
    )
    filename = f"{uuid_mod.uuid4().hex}.png"
    imagen_url = _upload_to_supabase(result["b64_data"], marca_id, filename) if result.get("b64_data") else result.get("url", "")
    img = repo.crear(
        db,
        {
            "marca_id": marca_id,
            "contenido_id": contenido_id,
            "prompt": result.get("revised_prompt", ""),
            "imagen_url": imagen_url,
            "tamano": size,
            "estilo": estilo,
        },
    )
    contenido_repo.actualizar_campos(db, obj, {"imagen_url": imagen_url})
    db.commit()
    return img


def generar_carrusel(db: Session, marca_id: UUID, contenido_id: UUID, num_slides: int = 5, estilo: str = "vivid", rol: str = "") -> dict:
    """Genera N slides para un carrusel."""
    from services.imagen.carrusel import generar_carrusel_impl

    return generar_carrusel_impl(db, marca_id, contenido_id, num_slides, estilo, rol)


def asociar_contenido(db: Session, marca_id: UUID, imagen_id: UUID, contenido_id: UUID) -> dict:
    """Asocia una imagen existente a un contenido."""
    img = repo.obtener(db, imagen_id, marca_id)
    if not img:
        raise AppError("Imagen no encontrada", "NOT_FOUND", 404)
    obj = contenido_repo.obtener(db, contenido_id, marca_id)
    if not obj:
        raise AppError("Contenido no encontrado", "NOT_FOUND", 404)
    img.contenido_id = contenido_id
    contenido_repo.actualizar_campos(db, obj, {"imagen_url": img.imagen_url})
    db.flush()
    db.commit()
    return {"imagen_id": str(imagen_id), "contenido_id": str(contenido_id), "imagen_url": img.imagen_url}


def listar(db: Session, marca_id: UUID) -> list[dict]:
    return repo.listar(db, marca_id)
