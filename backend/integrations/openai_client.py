"""
Cliente OpenAI para generación de imágenes con GPT Image 1.5 (gpt-image-1).
"""

import logging
from typing import Optional

import requests

from config.settings import get_settings

logger = logging.getLogger(__name__)

_IMAGE_MODEL = "gpt-image-1"
_TIMEOUT = 60


def _api_key(custom_key: Optional[str] = None) -> str:
    return custom_key or get_settings().OPENAI_API_KEY


def generar_imagen(
    prompt: str,
    size: str = "1024x1024",
    style: str = "vivid",
    quality: str = "high",
    custom_api_key: Optional[str] = None,
) -> dict:
    """
    Genera una imagen con GPT Image 1.5.

    Args:
        prompt: Descripción de la imagen
        size: 1024x1024, 1792x1024, 1024x1792
        style: vivid o natural
        quality: high o standard
        custom_api_key: Key propia del cliente (Premium)

    Returns:
        {"b64_data": "...", "revised_prompt": "..."}
    """
    key = _api_key(custom_api_key)
    if not key:
        raise OpenAIError("OPENAI_API_KEY no configurada", 500)

    logger.debug(f"[openai_client] generar_imagen — size={size}, style={style}")

    resp = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        json={
            "model": _IMAGE_MODEL,
            "prompt": prompt,
            "n": 1,
            "size": size,
            "quality": quality,
            "output_format": "png",
        },
        timeout=_TIMEOUT,
    )

    if resp.status_code != 200:
        body = {}
        try:
            body = resp.json()
        except Exception:
            pass
        msg = body.get("error", {}).get("message", f"OpenAI API error {resp.status_code}")
        logger.error(f"[openai_client] HTTP {resp.status_code} — {msg}")
        raise OpenAIError(msg, resp.status_code)

    data = resp.json()["data"][0]
    return {
        "b64_data": data.get("b64_json"),
        "url": data.get("url"),
        "revised_prompt": data.get("revised_prompt"),
    }


def generar_imagen_desde_marca(
    descripcion_usuario: str,
    perfil_marca: dict,
    size: str = "1024x1024",
    style: str = "vivid",
    custom_api_key: Optional[str] = None,
) -> dict:
    """
    Construye prompt enriquecido con el perfil de marca y genera imagen.

    Args:
        descripcion_usuario: Lo que el usuario quiere ver
        perfil_marca: Dict con nombre_marca, colores_marca, tono_voz, etc.
    """
    parts = [descripcion_usuario]

    nombre = perfil_marca.get("nombre_marca")
    if nombre:
        parts.append(f"Para la marca '{nombre}'.")

    colores = perfil_marca.get("colores_marca", [])
    if colores:
        parts.append(f"Paleta de colores: {', '.join(colores)}.")

    tono = perfil_marca.get("tono_voz")
    if tono:
        parts.append(f"Estética {tono}.")

    industria = perfil_marca.get("industria")
    if industria:
        parts.append(f"Industria: {industria}.")

    prompt = " ".join(parts)
    logger.debug(f"[openai_client] prompt enriquecido: {prompt[:100]}...")
    return generar_imagen(prompt, size=size, style=style, custom_api_key=custom_api_key)


class OpenAIError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)
