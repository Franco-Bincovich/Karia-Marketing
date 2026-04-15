"""
Cliente Anthropic para búsqueda de prospectos B2B con web search nativo.

Portado de KarIA Reach / integrations/claudeClient.js.
Usa el tool web_search_20250305 para que Claude busque en internet y encuentre
contactos con emails corporativos reales.

Flujo de respuesta con web search:
  La API retorna múltiples bloques en orden:
  1. server_tool_use  — consultas ejecutadas
  2. web_search_tool_result — resultados crudos
  3. text — JSON procesado por Claude
  Solo se procesa el último bloque de tipo "text".
"""

import json
import logging
import re
from typing import Any, Optional

import anthropic

from config.settings import get_settings

logger = logging.getLogger(__name__)

_SEARCH_MODEL = "claude-sonnet-4-20250514"
_WEB_SEARCH_TOOL = [{"type": "web_search_20250305", "name": "web_search"}]

_client: Optional[anthropic.Anthropic] = None


def _get_client() -> anthropic.Anthropic:
    """Retorna instancia lazy del cliente Anthropic."""
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=get_settings().ANTHROPIC_API_KEY)
    return _client


def _parse_json_array(text: str) -> Any:
    """Extrae un array JSON de la respuesta de Claude, tolerando texto extra."""
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\[[\s\S]*\]", text)
        if match:
            return json.loads(match.group(0))
        raise ValueError("La respuesta de Claude no contiene JSON válido")


def _parse_json_object(text: str) -> dict:
    """Extrae un objeto JSON de la respuesta de Claude, tolerando texto extra."""
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            return json.loads(match.group(0))
        raise ValueError("La respuesta de Claude no contiene JSON válido")


def buscar_contactos_ia(
    rubro: str,
    ubicacion: str,
    cantidad: int,
    prompt_personalizado: Optional[str] = None,
) -> list[dict]:
    """
    Busca prospectos B2B usando Claude con web search nativo.

    Args:
        rubro: Sector de las empresas a buscar (ej: "tecnología", "construcción")
        ubicacion: Ciudad, provincia o país (ej: "Buenos Aires", "Argentina")
        cantidad: Cantidad de contactos a generar (se clampea entre 5 y 50)
        prompt_personalizado: Instrucción extra para refinar la búsqueda

    Returns:
        Lista de dicts con claves: nombre, empresa, email_empresarial, cargo,
        telefono_empresa, confianza (0.0-1.0), origen ("ai").

    Raises:
        ValueError: Si Claude no retorna JSON válido
        anthropic.APIError: Si la API de Anthropic falla
    """
    cantidad = max(5, min(50, int(cantidad)))
    extra = f"\nINSTRUCCIÓN ADICIONAL: {prompt_personalizado}" if prompt_personalizado else ""

    logger.debug(f"[claude_client] buscar_contactos_ia — rubro={rubro!r}, ubicacion={ubicacion!r}, cantidad={cantidad}")

    prompt = f"""Sos un experto en prospección B2B. Generá una lista de contactos comerciales reales y relevantes.

PARÁMETROS DE BÚSQUEDA:
- Rubro: {rubro}
- Ubicación: {ubicacion}
- Cantidad de contactos: {cantidad}{extra}

INSTRUCCIONES:
- Generá exactamente {cantidad} contactos — decisores con poder de compra (dueños, gerentes, directores)
- Priorizá emails corporativos (no gmail, no hotmail)
- confianza entre 0.0 y 1.0 según la certeza del dato
- telefono_empresa es opcional — null si no está disponible con certeza
- email_empresarial es obligatorio — no incluir contacto si confianza < 0.5
- Responder SOLO con JSON, sin texto adicional

FORMATO:
[
  {{
    "nombre": "Nombre Apellido",
    "empresa": "Nombre Empresa",
    "email_empresarial": "email@empresa.com",
    "cargo": "Director Comercial",
    "telefono_empresa": "+54 11 1234-5678",
    "confianza": 0.85,
    "origen": "ai"
  }}
]"""

    message = _get_client().messages.create(
        model=_SEARCH_MODEL,
        max_tokens=2048,
        tools=_WEB_SEARCH_TOOL,
        messages=[{"role": "user", "content": prompt}],
    )

    text_blocks = [b for b in message.content if b.type == "text"]
    if not text_blocks:
        raise ValueError("[claude_client] La respuesta no contiene bloques de texto")

    response_text = text_blocks[-1].text
    logger.debug(f"[claude_client] Bloques: {[b.type for b in message.content]}")

    contactos = _parse_json_array(response_text)
    logger.debug(f"[claude_client] {len(contactos)} prospectos encontrados")
    return contactos


_NETWORK_RULES = {
    "instagram": "Máximo 2200 caracteres. Hashtags al final del copy (6-10 hashtags). Hook fuerte en la primera línea.",
    "facebook": "Texto conversacional y más largo. Sin límite estricto de hashtags. Invitá a interactuar.",
    "linkedin": "Tono profesional. Primera línea como gancho. Usá line breaks para legibilidad. 1-3 hashtags.",
    "tiktok": "Copy breve y directo. Máx 150 caracteres. Enfocado en el hook visual.",
    "twitter": "Máx 280 caracteres. Conciso e impactante. 1-2 hashtags como máximo.",
}


def generar_contenido_ia(
    red_social: str,
    formato: str,
    objetivo: str,
    tono: str,
    tema: str,
    memoria_marca: str,
    feedback_previo: Optional[str] = None,
    custom_api_key: Optional[str] = None,
) -> dict:
    """
    Genera 3 variantes (A/B/C) de contenido optimizado por red social.

    Cada variante incluye: copy, hashtags, call to action.
    Las variantes difieren en ángulo narrativo, estructura o tipo de apertura.

    Args:
        custom_api_key: Si se provee, usa esta key en vez de la default de Nexo

    Returns:
        Dict con: copy_a/b/c, hashtags_a/b/c, cta_a/b/c, variable_testeada
    """
    logger.debug(f"[claude_client] generar_contenido_ia — {red_social}/{formato}")

    network_rule = _NETWORK_RULES.get(red_social, "Adaptá la longitud al canal.")

    system_prompt = (
        f"Sos el Agente Contenido de Nexo Marketing. Generás copies de alta calidad para redes sociales.\n"
        f"Siempre generás TRES variantes (A, B y C) genuinamente diferentes — no levemente distintas.\n"
        f"Las variantes deben diferir en: ángulo narrativo, estructura, tono o tipo de apertura.\n"
        f"Cada variante tiene que ser tan buena como para publicarse sola.\n\n"
        f"REGLAS PARA {red_social.upper()}:\n{network_rule}\n\n"
        f"PERFIL DE MARCA:\n{memoria_marca}\n\n"
        f'Respondé SOLO con JSON válido con esta estructura exacta:\n'
        f'{{\n'
        f'  "copy_a": "texto completo de la variante A",\n'
        f'  "copy_b": "texto completo de la variante B",\n'
        f'  "copy_c": "texto completo de la variante C",\n'
        f'  "hashtags_a": "hashtags variante A",\n'
        f'  "hashtags_b": "hashtags variante B",\n'
        f'  "hashtags_c": "hashtags variante C",\n'
        f'  "cta_a": "call to action variante A",\n'
        f'  "cta_b": "call to action variante B",\n'
        f'  "cta_c": "call to action variante C",\n'
        f'  "variable_testeada": "qué variable diferencia las 3 variantes"\n'
        f"}}"
    )

    feedback_line = f"\nFEEDBACK PREVIO A INCORPORAR: {feedback_previo}" if feedback_previo else ""
    user_prompt = (
        f"Generá contenido para:\n"
        f"- Red social: {red_social}\n"
        f"- Formato: {formato}\n"
        f"- Objetivo: {objetivo}\n"
        f"- Tono: {tono}\n"
        f"- Tema: {tema}{feedback_line}"
    )

    client = _get_client()
    if custom_api_key:
        client = anthropic.Anthropic(api_key=custom_api_key)

    message = client.messages.create(
        model=_SEARCH_MODEL,
        max_tokens=3000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    text_blocks = [b for b in message.content if b.type == "text"]
    if not text_blocks:
        raise ValueError("[claude_client] La respuesta no contiene bloques de texto")

    resultado = _parse_json_object(text_blocks[-1].text)
    logger.debug(f"[claude_client] contenido generado — variable_testeada: {resultado.get('variable_testeada')!r}")
    return resultado


def sugerir_respuesta_onboarding(
    pregunta: str,
    contexto_respuestas: dict,
    preguntas: list,
    memoria: dict,
) -> str:
    """
    Sugiere una respuesta para una pregunta del onboarding basándose en el contexto.

    Args:
        pregunta: Texto de la pregunta a responder
        contexto_respuestas: Dict {id: respuesta} de lo ya respondido
        preguntas: Lista completa de preguntas para mapear IDs a textos
        memoria: Memoria de marca actual

    Returns:
        Texto de sugerencia para la respuesta
    """
    logger.debug("[claude_client] sugerir_respuesta_onboarding")

    # Build context from answered questions
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
        system=(
            "Sos un asistente de onboarding para marcas. "
            "Sugerí una respuesta concreta y útil basándote en el contexto de la marca. "
            "Respondé solo con el texto de la sugerencia, sin explicaciones ni prefijos."
        ),
        messages=[{"role": "user", "content": (
            f"Marca: {nombre}\n\n"
            f"Lo que ya sabemos de la marca:\n{contexto_texto}\n\n"
            f"Pregunta a responder: {pregunta}\n\n"
            f"Sugerí una respuesta apropiada:"
        )}],
    )

    text_blocks = [b for b in message.content if b.type == "text"]
    return text_blocks[-1].text.strip() if text_blocks else ""


def autocompletar_perfil_marca(nombre_marca: str) -> dict:
    """
    Busca información pública de una marca e intenta autocompletar respuestas del onboarding.

    Returns:
        Dict {pregunta_id: respuesta_sugerida} para las preguntas que pudo completar
    """
    logger.debug(f"[claude_client] autocompletar_perfil_marca — {nombre_marca!r}")

    message = _get_client().messages.create(
        model=_SEARCH_MODEL,
        max_tokens=2048,
        tools=_WEB_SEARCH_TOOL,
        messages=[{"role": "user", "content": (
            f"Investigá la marca '{nombre_marca}' en internet y completá la mayor cantidad "
            f"posible de estos campos basándote en información pública.\n\n"
            f"Campos a completar (usá el ID numérico como clave):\n"
            f'1: Nombre de la marca y a qué se dedica\n'
            f'2: Público objetivo\n'
            f'3: Problema que resuelve\n'
            f'5: Principales competidores\n'
            f'6: Propuesta de valor diferencial\n'
            f'8: Productos o servicios principales\n'
            f'10: Canales digitales donde tiene presencia\n\n'
            f"Respondé SOLO con un JSON con los IDs como clave y las respuestas como valor. "
            f"Solo incluí los campos donde encontraste información confiable.\n"
            f'Ejemplo: {{"1": "Nike es una marca de...", "2": "Deportistas..."}}'
        )}],
    )

    text_blocks = [b for b in message.content if b.type == "text"]
    if not text_blocks:
        return {}

    try:
        return _parse_json_object(text_blocks[-1].text)
    except (ValueError, json.JSONDecodeError):
        logger.warning("[claude_client] No se pudo parsear respuesta de autocompletado")
        return {}
