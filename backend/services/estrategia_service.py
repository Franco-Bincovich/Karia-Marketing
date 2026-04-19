"""Servicio del Agente Estrategia — análisis de competencia, plan de contenido, sugerencias."""

import json
import logging
from uuid import UUID

from sqlalchemy.orm import Session

from integrations.claude_client import _get_client, _SEARCH_MODEL, _WEB_SEARCH_TOOL, _parse_json_object
from middleware.error_handler import AppError
from repositories import estrategia_repository as repo
from repositories import memoria_marca_repository as memoria_repo

logger = logging.getLogger(__name__)


def _get_memoria(db: Session, marca_id: UUID) -> str:
    return memoria_repo.obtener_para_agente(db, marca_id)


def analizar_competencia(db: Session, marca_id: UUID) -> dict:
    """Usa Claude con web search para investigar competidores del perfil de marca."""
    memoria = memoria_repo.obtener_o_crear(db, marca_id)
    competidores = memoria.get("competidores")
    nombre = memoria.get("nombre_marca", "la marca")

    comp_text = ""
    if isinstance(competidores, dict) and competidores.get("respuesta"):
        comp_text = competidores["respuesta"]
    elif isinstance(competidores, str):
        comp_text = competidores

    if not comp_text:
        raise AppError("No hay competidores definidos en el perfil de marca", "NO_COMPETITORS", 400)

    message = _get_client().messages.create(
        model=_SEARCH_MODEL,
        max_tokens=2048,
        tools=_WEB_SEARCH_TOOL,
        messages=[{"role": "user", "content": (
            f"Analizá los competidores de '{nombre}': {comp_text}\n\n"
            f"Para cada competidor investigá:\n"
            f"- Presencia en redes sociales\n"
            f"- Tipo de contenido que publican\n"
            f"- Frecuencia de publicación\n"
            f"- Engagement aparente\n"
            f"- Fortalezas y debilidades vs {nombre}\n\n"
            f"Respondé con JSON: {{\"competidores\": [{{\"nombre\": ..., \"redes\": ..., "
            f"\"contenido\": ..., \"frecuencia\": ..., \"fortalezas\": [...], "
            f"\"debilidades\": [...], \"oportunidades_para_{nombre}\": [...]}}], "
            f"\"resumen\": \"...\"}}"
        )}],
    )

    text_blocks = [b for b in message.content if b.type == "text"]
    try:
        resultado = _parse_json_object(text_blocks[-1].text) if text_blocks else {}
    except (ValueError, json.JSONDecodeError):
        resultado = {"resumen": text_blocks[-1].text if text_blocks else "Sin resultado"}

    entry = repo.crear(db, {
        "marca_id": marca_id, "tipo": "analisis",
        "contenido": resultado, "periodo": None,
    })
    db.commit()
    return entry


def generar_plan_contenido(
    db: Session, marca_id: UUID, periodo: str = "semanal",
    red_social: str = "todas", formatos: list = None,
) -> dict:
    """Genera plan de contenido con filtros de red social y formatos."""
    memoria_text = _get_memoria(db, marca_id)
    memoria = memoria_repo.obtener_o_crear(db, marca_id)
    nombre = memoria.get("nombre_marca", "la marca")

    dias = {"diario": 7, "semanal": 7, "mensual": 30}.get(periodo, 7)
    formatos_permitidos = formatos or ["post", "carrusel", "reel", "story"]
    formatos_str = ", ".join(formatos_permitidos)

    red_instruccion = ""
    if red_social == "todas":
        red_instruccion = "Alterná entre Instagram y Facebook de forma equilibrada."
    else:
        red_instruccion = f"Todos los días deben ser para {red_social}."

    message = _get_client().messages.create(
        model=_SEARCH_MODEL,
        max_tokens=2048,
        system=(
            f"Sos el agente de estrategia de {nombre}. Generás planes de contenido "
            f"concretos y accionables.\n\nPERFIL DE MARCA:\n{memoria_text}"
        ),
        messages=[{"role": "user", "content": (
            f"Generá un plan de contenido {periodo} ({dias} días) para {nombre}.\n\n"
            f"RESTRICCIONES:\n"
            f"- Redes sociales: {red_instruccion}\n"
            f"- Formatos permitidos: {formatos_str}. NO uses otros formatos.\n\n"
            f"Para cada día incluí:\n"
            f"- Día (número)\n"
            f"- Red social\n"
            f"- Formato (solo de los permitidos: {formatos_str})\n"
            f"- Tema\n"
            f"- Objetivo\n"
            f"- Copy sugerido breve\n\n"
            f"Respondé con JSON: {{\"plan\": [{{\"dia\": 1, \"red_social\": ..., "
            f"\"formato\": ..., \"tema\": ..., \"objetivo\": ..., \"copy_sugerido\": ...}}], "
            f"\"resumen\": \"...\"}}"
        )}],
    )

    text_blocks = [b for b in message.content if b.type == "text"]
    try:
        resultado = _parse_json_object(text_blocks[-1].text) if text_blocks else {}
    except (ValueError, json.JSONDecodeError):
        resultado = {"resumen": text_blocks[-1].text if text_blocks else "Sin resultado"}

    entry = repo.crear(db, {
        "marca_id": marca_id, "tipo": "plan",
        "contenido": resultado, "periodo": periodo,
    })
    db.commit()
    return entry


def activar_plan(db: Session, marca_id: UUID, plan_id: UUID) -> dict:
    """Activa un plan y desactiva los anteriores."""
    result = repo.activar_plan(db, plan_id, marca_id)
    if not result:
        from middleware.error_handler import AppError
        raise AppError("Plan no encontrado", "NOT_FOUND", 404)
    db.commit()
    return result


def obtener_plan_activo(db: Session, marca_id: UUID) -> dict:
    """Retorna el plan de contenido activo de la marca."""
    return repo.obtener_plan_activo(db, marca_id)


def sugerir_acciones(db: Session, marca_id: UUID) -> dict:
    """Sugiere acciones estratégicas basadas en el perfil de marca."""
    memoria_text = _get_memoria(db, marca_id)
    memoria = memoria_repo.obtener_o_crear(db, marca_id)
    nombre = memoria.get("nombre_marca", "la marca")

    message = _get_client().messages.create(
        model=_SEARCH_MODEL,
        max_tokens=1500,
        system=(
            f"Sos el agente de estrategia de {nombre}. Sugerís acciones concretas "
            f"y priorizadas.\n\nPERFIL DE MARCA:\n{memoria_text}"
        ),
        messages=[{"role": "user", "content": (
            f"Proponé 5 acciones estratégicas concretas para {nombre} basándote "
            f"en su perfil de marca.\n\n"
            f"Para cada acción incluí: título, descripción, prioridad (alta/media/baja), "
            f"plazo estimado, impacto esperado.\n\n"
            f"Respondé con JSON: {{\"sugerencias\": [{{\"titulo\": ..., \"descripcion\": ..., "
            f"\"prioridad\": ..., \"plazo\": ..., \"impacto\": ...}}]}}"
        )}],
    )

    text_blocks = [b for b in message.content if b.type == "text"]
    try:
        resultado = _parse_json_object(text_blocks[-1].text) if text_blocks else {}
    except (ValueError, json.JSONDecodeError):
        resultado = {"sugerencias": [{"titulo": text_blocks[-1].text if text_blocks else "Sin resultado"}]}

    entry = repo.crear(db, {
        "marca_id": marca_id, "tipo": "sugerencia",
        "contenido": resultado,
    })
    db.commit()
    return entry


def listar_sugerencias(db: Session, marca_id: UUID) -> list[dict]:
    return repo.listar(db, marca_id, tipo="sugerencia")


def marcar_implementada(db: Session, marca_id: UUID, estrategia_id: UUID) -> dict:
    result = repo.marcar_implementada(db, estrategia_id, marca_id)
    if not result:
        raise AppError("Estrategia no encontrada", "NOT_FOUND", 404)
    db.commit()
    return result
