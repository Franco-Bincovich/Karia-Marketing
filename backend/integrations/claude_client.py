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
