"""Cliente para Leonardo AI — generación de imágenes."""

import logging
import re
import time
from typing import Optional

import requests

from config.settings import get_settings

logger = logging.getLogger(__name__)

_BASE_URL = "https://cloud.leonardo.ai/api/rest/v1"
_TIMEOUT = 60
_POLL_INTERVAL = 3
_MAX_POLLS = 40

# Leonardo Lucid Origin — mejor adherencia a paleta restrictiva
_DEFAULT_MODEL = "05ce0082-2d80-4a2d-8653-4d1c85e2418e"

_SIZE_MAP = {
    "1024x1024": (1024, 1024),
    "1792x1024": (1472, 832),
    "1024x1792": (832, 1472),
}

_DEFAULT_PALETTE = ["#09090B", "#FF6B00", "#FFFFFF", "#FAC6A1"]


def _headers(custom_key: Optional[str] = None) -> dict:
    key = custom_key or get_settings().LEONARDO_API_KEY
    return {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}


class LeonardoError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def _strict_negative(is_placa: bool = False) -> str:
    """Negative prompt. Para placa: estricto. Para elaborada: permisivo."""
    if is_placa:
        return (
            "text, letters, numbers, typography, words, writing, "
            "illustrations, icons, decorative elements, people, faces, "
            "cyan, magenta, pink, rainbow, multicolor, oversaturated, "
            "blurry, low quality, watermark, signature, corrupted text, "
            "distorted letters, random symbols, cluttered, busy background"
        )
    return (
        "text in image, written words, typography, logos, watermark, "
        "corrupted letters, distorted text, random symbols, fake labels, "
        "flat vector illustration, cartoon style, abstract geometric shapes, "
        "oversaturated rainbow, cyan, magenta, neon pink, "
        "blurry, low quality, ugly, deformed hands, extra fingers, "
        "amateur photography, stock photo watermark, signature"
    )


def _extract_palette(perfil_marca: dict) -> list:
    """Extrae HEX del perfil de marca. Fallback a paleta NEXO default."""
    raw = perfil_marca.get("colores_marca", [])
    text = " ".join(raw) if isinstance(raw, list) else str(raw or "")
    hex_codes = re.findall(r"#[0-9A-Fa-f]{6}", text)
    return hex_codes if hex_codes else _DEFAULT_PALETTE


def _build_brand_prompt(descripcion: str, palette: list, is_placa: bool, perfil_marca: dict = None, formato: str = "post") -> str:
    """
    Construye el prompt final para Leonardo.
    - Para placa: fondo texturado vacío listo para overlay.
    - Para elaborada: traduce el concepto a una escena realista de
      marketing usando Claude Haiku, y le suma la paleta como atmósfera.
    """
    bg = palette[0] if palette else "#09090B"
    accent = palette[1] if len(palette) > 1 else "#FF6B00"
    allowed = ", ".join(palette[:4])

    if is_placa:
        return (
            f"Minimal empty poster background with subtle geometric texture. "
            f"Dark matte background {bg} with a very subtle {accent} "
            f"light leak in one corner only. Large empty central area with "
            f"intentional negative space, ready to receive text overlay. "
            f"Strictly monochromatic — only these hex colors allowed: {allowed}. "
            f"Absolutely nothing else. No text, no icons, no people, "
            f"no illustrations, no dashboards. Editorial, minimalist, "
            f"professional brand aesthetic, high contrast."
        )

    # Elaborada: traducir concepto a escena realista usando Claude Haiku
    try:
        from integrations.claude_client import traducir_concepto_a_prompt_visual

        visual_scene = traducir_concepto_a_prompt_visual(
            descripcion,
            perfil_marca or {},
            formato=formato,
        )
        logger.info("[leonardo] escena traducida: %s", visual_scene[:120])
    except Exception as e:
        logger.warning("[leonardo] fallback prompt sin traductor: %s", e)
        visual_scene = (
            f"Professional marketing photograph representing the concept of "
            f"{(descripcion or '').strip()[:200]}. Realistic scene with people, "
            f"devices or office environment. Cinematic lighting, shot on 35mm, "
            f"high detail, natural composition."
        )

    return (
        f"{visual_scene} "
        f"Color atmosphere: dark {bg} ambient tones with warm {accent} "
        f"accent lighting (window light, screen glow, or subtle rim light). "
        f"Brand palette hints: {allowed}. "
        f"Photographic realism, editorial marketing style, not abstract, "
        f"not geometric illustration. Avoid flat design, avoid illustrations "
        f"of text, avoid posters with words."
    )


def generar_imagen(
    prompt: str,
    size: str = "1024x1024",
    style: str = "vivid",
    quality: str = "high",
    custom_api_key: Optional[str] = None,
    tipo: str = "elaborada",
) -> dict:
    """Genera imagen con Leonardo AI. Retorna {url, revised_prompt, b64_data}."""
    key = custom_api_key or get_settings().LEONARDO_API_KEY
    if not key:
        raise LeonardoError("LEONARDO_API_KEY no configurada", 500)

    w, h = _SIZE_MAP.get(size, (1024, 1024))
    headers = _headers(key)
    is_placa = tipo == "placa"

    payload = {
        "prompt": prompt,
        "negative_prompt": _strict_negative(is_placa),
        "width": w,
        "height": h,
        "modelId": _DEFAULT_MODEL,
        "num_images": 1,
        "guidance_scale": 3.5 if is_placa else 3,
        "num_inference_steps": 30,
        "alchemy": False,
        "presetStyle": "DYNAMIC",
    }

    resp = requests.post(
        f"{_BASE_URL}/generations",
        headers=headers,
        json=payload,
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

    logger.info("[leonardo] Gen iniciada: %s (%dx%d, tipo=%s)", generation_id, w, h, tipo)
    logger.debug("[leonardo] prompt: %s", prompt[:200])

    for _ in range(_MAX_POLLS):
        time.sleep(_POLL_INTERVAL)
        poll = requests.get(
            f"{_BASE_URL}/generations/{generation_id}",
            headers=headers,
            timeout=_TIMEOUT,
        )
        if poll.status_code != 200:
            continue
        data = poll.json().get("generations_by_pk", {})
        status = data.get("status")

        if status == "COMPLETE":
            images = data.get("generated_images", [])
            if images:
                url = images[0].get("url", "")
                logger.info("[leonardo] Imagen OK: %s", url[:80])
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
    tipo: str = "elaborada",
) -> dict:
    """Genera imagen con paleta del perfil — escena realista para elaborada."""
    palette = _extract_palette(perfil_marca)
    # inferir formato desde el size para pasar al traductor
    formato_map = {
        "1024x1024": "post",
        "1024x1792": "historia",
        "1792x1024": "facebook_post",
    }
    formato = formato_map.get(size, "post")
    prompt = _build_brand_prompt(
        descripcion_usuario,
        palette,
        is_placa=(tipo == "placa"),
        perfil_marca=perfil_marca,
        formato=formato,
    )
    return generar_imagen(
        prompt,
        size=size,
        style=style,
        custom_api_key=custom_api_key,
        tipo=tipo,
    )
