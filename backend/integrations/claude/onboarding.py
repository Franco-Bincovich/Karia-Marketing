"""Funciones Claude para onboarding — sugerencias y autocompletado."""

import json
import logging

from integrations.claude.base import (
    _SEARCH_MODEL,
    _WEB_SEARCH_TOOL,
    _get_client,
    _parse_json_object,
)

logger = logging.getLogger(__name__)


def sugerir_respuesta_onboarding(pregunta: str, contexto_respuestas: dict, preguntas: list, memoria: dict) -> str:
    """Sugiere una respuesta para una pregunta del onboarding."""
    contexto_lines = []
    id_to_pregunta = {str(p["id"]): p["pregunta"] for p in preguntas}
    for pid, resp in contexto_respuestas.items():
        if resp and pid in id_to_pregunta:
            contexto_lines.append(f"- {id_to_pregunta[pid]}: {resp}")

    nombre = memoria.get("nombre_marca", "la marca")
    contexto_texto = "\n".join(contexto_lines) if contexto_lines else "No hay respuestas previas."

    message = _get_client().messages.create(
        model=_SEARCH_MODEL,
        max_tokens=500,
        system="Sos un asistente de onboarding para marcas. Sugerí una respuesta concreta basándote en el contexto. Sin explicaciones ni prefijos.",
        messages=[{"role": "user", "content": f"Marca: {nombre}\n\nContexto:\n{contexto_texto}\n\nPregunta: {pregunta}\n\nSugerí:"}],
    )
    text_blocks = [b for b in message.content if b.type == "text"]
    return text_blocks[-1].text.strip() if text_blocks else ""


def autocompletar_perfil_marca(nombre_marca: str) -> dict:
    """Busca info pública de una marca e intenta autocompletar el onboarding."""
    message = _get_client().messages.create(
        model=_SEARCH_MODEL,
        max_tokens=2048,
        tools=_WEB_SEARCH_TOOL,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Investigá la marca '{nombre_marca}' en internet y completá estos campos:\n"
                    f"1: Nombre y a qué se dedica\n2: Público objetivo\n3: Problema que resuelve\n"
                    f"5: Competidores\n6: Propuesta de valor\n8: Productos principales\n10: Canales digitales\n\n"
                    f"Respondé SOLO con JSON {{id: respuesta}}. Solo campos con info confiable."
                ),
            }
        ],
    )
    text_blocks = [b for b in message.content if b.type == "text"]
    if not text_blocks:
        return {}
    try:
        return _parse_json_object(text_blocks[-1].text)
    except (ValueError, json.JSONDecodeError):
        logger.warning("[claude] No se pudo parsear autocompletado")
        return {}
