"""Generación de carruseles — copies + imágenes por slide."""

import logging
import uuid as uuid_mod
from uuid import UUID

from sqlalchemy.orm import Session

from middleware.error_handler import AppError
from repositories import contenido_repository as contenido_repo
from repositories import memoria_marca_repository as memoria_repo
from services.imagen.helpers import custom_openai_key, gen_imagen_marca, get_context
from services.imagen.storage import upload_to_supabase

logger = logging.getLogger(__name__)


def generar_carrusel_impl(
    db: Session,
    marca_id: UUID,
    contenido_id: UUID,
    num_slides: int = 5,
    estilo: str = "vivid",
    rol: str = "",
) -> dict:
    """Genera N slides para un carrusel: copies + imágenes por slide."""
    cliente, _ = get_context(db, marca_id)
    openai_key = custom_openai_key(cliente, rol)

    obj = contenido_repo.obtener(db, contenido_id, marca_id)
    if not obj:
        raise AppError("Contenido no encontrado", "NOT_FOUND", 404)

    num_slides = max(2, min(10, num_slides))
    variante = obj.variante_seleccionada or "a"
    copy_text = getattr(obj, f"copy_{variante}") or obj.copy_a or ""
    perfil = memoria_repo.obtener_o_crear(db, marca_id)

    slides_data = _generate_slide_copies(db, marca_id, copy_text, num_slides)

    from models.contenido_models import CarruselSlideMkt

    slides_result = []
    for i, slide in enumerate(slides_data):
        img_url = _generate_slide_image(db, cliente.id, slide, perfil, estilo, openai_key, marca_id)
        slide_obj = CarruselSlideMkt(
            contenido_id=contenido_id,
            orden=i + 1,
            imagen_url=img_url,
            copy_slide=slide.get("copy_slide", f"Slide {i + 1}"),
        )
        db.add(slide_obj)
        db.flush()
        slides_result.append({"id": str(slide_obj.id), "orden": slide_obj.orden, "imagen_url": img_url, "copy_slide": slide_obj.copy_slide})

    if slides_result and slides_result[0].get("imagen_url"):
        contenido_repo.actualizar_campos(db, obj, {"imagen_url": slides_result[0]["imagen_url"]})

    db.commit()
    return {"contenido_id": str(contenido_id), "num_slides": len(slides_result), "slides": slides_result}


def _generate_slide_copies(db: Session, marca_id: UUID, copy_text: str, num_slides: int) -> list:
    """Usa Claude para generar copies de cada slide."""
    from integrations.claude_client import _SEARCH_MODEL, _get_client, _parse_json_object

    client = _get_client()
    message = client.messages.create(
        model=_SEARCH_MODEL,
        max_tokens=2048,
        system=f"Sos un experto en carruseles de Instagram. Perfil: {memoria_repo.obtener_para_agente(db, marca_id)}",
        messages=[
            {
                "role": "user",
                "content": (
                    f"Creá un carrusel de {num_slides} slides basado en:\n\n{copy_text}\n\n"
                    f"Para cada slide: copy_slide (max 100 chars) + descripcion_imagen.\n"
                    f'JSON: {{"slides": [{{"copy_slide": "...", "descripcion_imagen": "..."}}]}}'
                ),
            }
        ],
    )
    text_blocks = [b for b in message.content if b.type == "text"]
    try:
        data = _parse_json_object(text_blocks[-1].text)
        return data.get("slides", [])[:num_slides]
    except Exception:
        return [{"copy_slide": f"Slide {i + 1}", "descripcion_imagen": copy_text[:200]} for i in range(num_slides)]


def _generate_slide_image(db, cliente_id, slide, perfil, estilo, openai_key, marca_id) -> str:
    """Genera imagen para un slide individual."""
    try:
        result = gen_imagen_marca(
            db,
            cliente_id,
            slide.get("descripcion_imagen", "Slide de carrusel"),
            perfil,
            size="1024x1024",
            style=estilo,
            openai_key=openai_key,
        )
        filename = f"{uuid_mod.uuid4().hex}.png"
        if result.get("b64_data"):
            return upload_to_supabase(result["b64_data"], marca_id, filename)
        return result.get("url", "")
    except Exception as e:
        logger.warning("Error generando slide: %s", e)
        return ""
