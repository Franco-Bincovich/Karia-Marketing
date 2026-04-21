"""Agente Copy Visual — aplica texto sobre imágenes generadas."""

import io
import logging
import os
import re
import textwrap
from pathlib import Path
from typing import Optional

import requests
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

_FONTS_DIR = Path(__file__).resolve().parent.parent.parent / "assets" / "fonts"
_BARLOW_PATH = str(_FONTS_DIR / "Barlow-ExtraBold.ttf")
_LOGO_COLOR = (102, 102, 102)


def _get_font(size: int) -> ImageFont.FreeTypeFont:
    if os.path.isfile(_BARLOW_PATH):
        try:
            return ImageFont.truetype(_BARLOW_PATH, size)
        except (OSError, IOError):
            pass
    for path in ["/System/Library/Fonts/Helvetica.ttc",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def _hex_to_rgb(h: str) -> tuple:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _resolve_palette(colores_hex: list) -> dict:
    colors = colores_hex or ["#FF6B00"]
    accent = _hex_to_rgb(colors[0])
    secondary = _hex_to_rgb(colors[1]) if len(colors) > 1 else accent
    return {"accent": accent, "secondary": secondary}


def aplicar_texto(
    imagen_url: str,
    brief_creativo: dict,
    perfil_marca: dict,
    width: int,
    height: int,
) -> bytes:
    """
    Descarga imagen y superpone texto del brief con jerarquía tipográfica.

    Returns:
        bytes PNG de la imagen final con texto.
    """
    colores_raw = perfil_marca.get("colores_marca", [])
    colores_str = " ".join(colores_raw) if isinstance(colores_raw, list) else str(colores_raw or "")
    hex_codes = re.findall(r"#[0-9A-Fa-f]{6}", colores_str)
    pal = _resolve_palette(hex_codes)

    texto_principal = brief_creativo.get("texto_principal", "")
    texto_secundario = brief_creativo.get("texto_secundario", "")

    if not texto_principal:
        logger.info("[copy_visual] sin texto — retornando imagen sin overlay")
        resp = requests.get(imagen_url, timeout=30)
        resp.raise_for_status()
        return resp.content

    # Descargar imagen base
    try:
        resp = requests.get(imagen_url, timeout=30)
        resp.raise_for_status()
        img = Image.open(io.BytesIO(resp.content)).convert("RGB")
        img = img.resize((width, height), Image.LANCZOS)
    except Exception as e:
        logger.error("[copy_visual] error descargando imagen: %s", e)
        img = Image.new("RGB", (width, height), (9, 9, 11))

    draw = ImageDraw.Draw(img)

    # Título — grande
    title_size = int(width * 0.07) if len(texto_principal) <= 40 else int(width * 0.05)
    font_title = _get_font(title_size)
    lines = textwrap.wrap(texto_principal, width=18 if len(texto_principal) <= 40 else 26)
    line_h = title_size * 1.3
    total_h = len(lines) * line_h
    sub_h = int(width * 0.03) * 1.5 if texto_secundario else 0
    start_y = (height - total_h - sub_h) / 2 - height * 0.02
    shadow = max(2, title_size // 18)

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font_title)
        x = (width - (bbox[2] - bbox[0])) / 2
        y = start_y + i * line_h
        draw.text((x + shadow, y + shadow), line, fill=(0, 0, 0), font=font_title)
        draw.text((x, y), line, fill=pal["accent"], font=font_title)

    # Subtítulo — pequeño, debajo
    if texto_secundario:
        sub_size = int(width * 0.03)
        font_sub = _get_font(sub_size)
        sub_y = start_y + total_h + height * 0.02
        bbox = draw.textbbox((0, 0), texto_secundario, font=font_sub)
        x = (width - (bbox[2] - bbox[0])) / 2
        draw.text((x + 1, sub_y + 1), texto_secundario, fill=(0, 0, 0), font=font_sub)
        draw.text((x, sub_y), texto_secundario, fill=pal["secondary"], font=font_sub)

    # Línea decorativa
    deco_y = start_y + total_h + sub_h + height * 0.04
    line_w = min(width * 0.25, 250)
    line_x = (width - line_w) / 2
    draw.rectangle([line_x, deco_y, line_x + line_w, deco_y + 3], fill=pal["accent"])

    # NEXO logo
    font_logo = _get_font(int(width * 0.022))
    logo_bbox = draw.textbbox((0, 0), "NEXO", font=font_logo)
    draw.text((width - (logo_bbox[2] - logo_bbox[0]) - width * 0.04,
               height - height * 0.05), "NEXO", fill=_LOGO_COLOR, font=font_logo)

    buf = io.BytesIO()
    img.save(buf, format="PNG", quality=95)
    buf.seek(0)
    logger.info("[copy_visual] texto aplicado — %dx%d", width, height)
    return buf.getvalue()
