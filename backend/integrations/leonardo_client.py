"""Cliente para Leonardo AI — generación de imágenes."""

import logging
import time
from typing import Optional

import requests

from config.settings import get_settings

logger = logging.getLogger(__name__)

_BASE_URL = "https://cloud.leonardo.ai/api/rest/v1"
_DEFAULT_MODEL = "b24e16ff-06e3-43eb-8d33-4416c2d75876"  # Leonardo Phoenix
_TIMEOUT = 60
_POLL_INTERVAL = 3
_MAX_POLLS = 40  # 40 * 3s = 2 min max

# Leonardo no soporta todos los tamaños — mapear a los más cercanos
_SIZE_MAP = {
    "1024x1024": (1024, 1024),
    "1792x1024": (1472, 832),
    "1024x1792": (832, 1472),
}


def _headers(custom_key: Optional[str] = None) -> dict:
    key = custom_key or get_settings().LEONARDO_API_KEY
    return {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}


class LeonardoError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def generar_imagen(
    prompt: str,
    size: str = "1024x1024",
    style: str = "vivid",
    quality: str = "high",
    custom_api_key: Optional[str] = None,
) -> dict:
    """
    Genera imagen con Leonardo AI.

    Returns:
        {"url": "https://...", "revised_prompt": "..."}
        Compatible con la interfaz de openai_client.
    """
    key = custom_api_key or get_settings().LEONARDO_API_KEY
    if not key:
        raise LeonardoError("LEONARDO_API_KEY no configurada", 500)

    w, h = _SIZE_MAP.get(size, (1024, 1024))
    headers = _headers(key)

    # 1. Start generation
    resp = requests.post(
        f"{_BASE_URL}/generations",
        headers=headers,
        json={
            "prompt": prompt,
            "width": w,
            "height": h,
            "modelId": _DEFAULT_MODEL,
            "num_images": 1,
        },
        timeout=_TIMEOUT,
    )

    if resp.status_code != 200:
        body = {}
        try:
            body = resp.json()
        except Exception:
            pass
        msg = body.get("error", f"Leonardo API error {resp.status_code}")
        logger.error("[leonardo] HTTP %s — %s", resp.status_code, msg)
        raise LeonardoError(msg, resp.status_code)

    generation_id = resp.json().get("sdGenerationJob", {}).get("generationId")
    if not generation_id:
        raise LeonardoError("No se obtuvo generationId de Leonardo", 500)

    logger.info("[leonardo] Generación iniciada: %s (%dx%d)", generation_id, w, h)

    # 2. Poll until complete
    for _ in range(_MAX_POLLS):
        time.sleep(_POLL_INTERVAL)
        poll = requests.get(f"{_BASE_URL}/generations/{generation_id}", headers=headers, timeout=_TIMEOUT)
        if poll.status_code != 200:
            continue
        data = poll.json().get("generations_by_pk", {})
        status = data.get("status")

        if status == "COMPLETE":
            images = data.get("generated_images", [])
            if images:
                url = images[0].get("url", "")
                logger.info("[leonardo] Imagen generada: %s", url[:80])
                return {"url": url, "revised_prompt": prompt, "b64_data": None}
            raise LeonardoError("Generación completa pero sin imágenes", 500)

        if status == "FAILED":
            raise LeonardoError("La generación falló en Leonardo", 500)

    raise LeonardoError("Timeout esperando generación de Leonardo", 504)


def generar_imagen_desde_marca(
    descripcion_usuario: str,
    perfil_marca: dict,
    size: str = "1024x1024",
    style: str = "vivid",
    custom_api_key: Optional[str] = None,
) -> dict:
    """Construye prompt enriquecido con perfil de marca y genera imagen."""
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
    logger.debug("[leonardo] prompt enriquecido: %s", prompt[:100])
    return generar_imagen(prompt, size=size, style=style, custom_api_key=custom_api_key)
