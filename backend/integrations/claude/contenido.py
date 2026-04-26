"""Funciones Claude para generación de contenido y prospección."""

import logging
from typing import Optional

import anthropic

from integrations.claude.base import (
    _SEARCH_MODEL,
    _WEB_SEARCH_TOOL,
    _get_client,
    _parse_json_array,
    _parse_json_object,
)

logger = logging.getLogger(__name__)

_NETWORK_RULES = {
    "instagram": "Máximo 2200 caracteres. Hashtags al final (6-10). Hook fuerte en la primera línea.",
    "facebook": "Texto conversacional y más largo. Sin límite estricto de hashtags. Invitá a interactuar.",
    "linkedin": "Tono profesional. Primera línea como gancho. 1-3 hashtags.",
    "tiktok": "Copy breve y directo. Máx 150 caracteres. Enfocado en el hook visual.",
    "twitter": "Máx 280 caracteres. Conciso e impactante. 1-2 hashtags.",
}


def buscar_contactos_ia(rubro: str, ubicacion: str, cantidad: int, prompt_personalizado: Optional[str] = None) -> list[dict]:
    """Busca prospectos B2B usando Claude con web search nativo."""
    cantidad = max(5, min(50, int(cantidad)))
    extra = f"\nINSTRUCCIÓN ADICIONAL: {prompt_personalizado}" if prompt_personalizado else ""

    prompt = (
        f"Sos un experto en prospección B2B. Generá una lista de contactos comerciales reales.\n\n"
        f"PARÁMETROS: Rubro: {rubro}, Ubicación: {ubicacion}, Cantidad: {cantidad}{extra}\n\n"
        f"INSTRUCCIONES:\n- Exactamente {cantidad} contactos decisores\n"
        f"- Priorizá emails corporativos\n- confianza 0.0-1.0\n- Respondé SOLO JSON\n\n"
        f'FORMATO: [{{"nombre":"...","empresa":"...","email_empresarial":"...","cargo":"...","telefono_empresa":"...","confianza":0.85,"origen":"ai"}}]'
    )

    message = _get_client().messages.create(
        model=_SEARCH_MODEL,
        max_tokens=2048,
        tools=_WEB_SEARCH_TOOL,
        messages=[{"role": "user", "content": prompt}],
    )
    text_blocks = [b for b in message.content if b.type == "text"]
    if not text_blocks:
        raise ValueError("[claude] La respuesta no contiene texto")
    return _parse_json_array(text_blocks[-1].text)


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
    """Genera 3 variantes (A/B/C) de contenido optimizado por red social."""
    network_rule = _NETWORK_RULES.get(red_social, "Adaptá la longitud al canal.")

    system_prompt = (
        f"Sos el Agente Contenido de Nexo Marketing. Generás copies de alta calidad.\n"
        f"Siempre generás TRES variantes (A, B y C) genuinamente diferentes.\n\n"
        f"REGLAS PARA {red_social.upper()}:\n{network_rule}\n\n"
        f"PERFIL DE MARCA:\n{memoria_marca}\n\n"
        f"Respondé SOLO con JSON válido con: copy_a/b/c, hashtags_a/b/c, cta_a/b/c, variable_testeada"
    )

    feedback_line = f"\nFEEDBACK: {feedback_previo}" if feedback_previo else ""
    user_prompt = f"Red: {red_social}\nFormato: {formato}\nObjetivo: {objetivo}\nTono: {tono}\nTema: {tema}{feedback_line}"

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
        raise ValueError("[claude] La respuesta no contiene texto")
    return _parse_json_object(text_blocks[-1].text)
