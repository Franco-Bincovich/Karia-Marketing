"""Agente Visual — genera imágenes a partir de instrucciones del Director de Arte."""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Mapeo formato → size key de Leonardo
_FORMATO_SIZE = {
    "post": "1024x1024",
    "carrusel": "1024x1024",
    "historia": "1024x1792",
    "reel": "1024x1792",
    "facebook_post": "1792x1024",
}


def generar(
    brief_creativo: dict,
    perfil_marca: dict,
    leo_key: Optional[str] = None,
) -> dict:
    """
    Genera imagen según instrucciones del Director de Arte.

    Args:
        brief_creativo: dict del director de arte con concepto_visual, mood, etc.
        perfil_marca: perfil de marca para paleta y contexto
        leo_key: API key de Leonardo

    Returns:
        dict con {url, revised_prompt, b64_data} de leonardo_client
    """
    tipo = brief_creativo.get("tipo", "elaborada")
    formato = brief_creativo.get("referencia_formato", "post")
    size = _FORMATO_SIZE.get(formato, "1024x1024")

    if tipo == "placa":
        return _generar_fondo_placa(brief_creativo, perfil_marca, leo_key, size)

    return _generar_elaborada(brief_creativo, perfil_marca, leo_key, size)


def _generar_elaborada(brief: dict, perfil: dict, leo_key: str, size: str) -> dict:
    """Genera imagen elaborada (escena realista de marketing)."""
    from integrations.leonardo_client import LeonardoError, generar_imagen_desde_marca

    concepto = brief.get("concepto_visual", "")
    mood = brief.get("mood", "")
    prompt_enriquecido = f"{concepto}. Mood: {mood}." if mood else concepto

    logger.info("[agente_visual] elaborada — prompt: %s", prompt_enriquecido[:100])

    try:
        return generar_imagen_desde_marca(
            prompt_enriquecido,
            perfil,
            size=size,
            style="vivid",
            custom_api_key=leo_key,
            tipo="elaborada",
        )
    except LeonardoError:
        raise
    except Exception as e:
        logger.error("[agente_visual] error inesperado: %s", e)
        raise


def _generar_fondo_placa(brief: dict, perfil: dict, leo_key: str, size: str) -> dict:
    """Genera fondo abstracto para placa (sin texto, listo para overlay)."""
    from integrations.leonardo_client import LeonardoError, generar_imagen_desde_marca

    concepto = brief.get("concepto_visual", "")
    prompt_fondo = f"Abstract background inspired by: {concepto}. Empty central area for text overlay. No text, no letters."

    logger.info("[agente_visual] fondo placa — prompt: %s", prompt_fondo[:100])

    try:
        return generar_imagen_desde_marca(
            prompt_fondo,
            perfil,
            size=size,
            style="vivid",
            custom_api_key=leo_key,
            tipo="placa",
        )
    except LeonardoError:
        raise
    except Exception as e:
        logger.error("[agente_visual] error fondo placa: %s", e)
        raise
