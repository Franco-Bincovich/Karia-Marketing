"""Generador de placas con texto — fondo abstracto Leonardo + texto Pillow."""

import io
import logging
import os
import textwrap
from pathlib import Path
from typing import Optional

import requests
from PIL import Image, ImageDraw, ImageFilter, ImageFont

logger = logging.getLogger(__name__)

_FONTS_DIR = Path(__file__).resolve().parent.parent / "assets" / "fonts"
_BARLOW_PATH = str(_FONTS_DIR / "Barlow-ExtraBold.ttf")

_BG_COLOR = "#09090B"
_ACCENT_COLOR = "#FF6B00"
_LOGO_COLOR = "#666666"


def _get_font(size: int) -> ImageFont.FreeTypeFont:
    """Carga Barlow ExtraBold embebido en el proyecto."""
    if os.path.isfile(_BARLOW_PATH):
        try:
            font = ImageFont.truetype(_BARLOW_PATH, size)
            logger.debug("[placa] usando Barlow ExtraBold @ %dpx", size)
            return font
        except (OSError, IOError) as e:
            logger.error("[placa] Barlow existe pero no carga: %s", e)
    else:
        logger.error("[placa] FALTA el archivo %s", _BARLOW_PATH)

    for path in [
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]:
        try:
            font = ImageFont.truetype(path, size)
            logger.warning("[placa] FALLBACK — usando %s", path)
            return font
        except (OSError, IOError):
            continue
    logger.warning("[placa] usando ImageFont.load_default()")
    return ImageFont.load_default()


def _download_image(url: str, timeout: int = 30) -> Image.Image:
    """Descarga imagen desde URL y la retorna como PIL Image."""
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    return Image.open(io.BytesIO(resp.content)).convert("RGB")


def _generate_leonardo_background(
    texto: str,
    colores_hex: list,
    width: int,
    height: int,
    leonardo_api_key: str,
    size_key: str = "1024x1024",
) -> Optional[Image.Image]:
    """Genera fondo abstracto con Leonardo AI y lo retorna como PIL Image."""
    from integrations.leonardo_client import generar_imagen, LeonardoError

    accent = colores_hex[0] if colores_hex else _ACCENT_COLOR
    prompt = (
        f"Abstract dark background for a minimalist poster. "
        f"Smooth gradients, subtle light effects, bokeh, geometric shapes. "
        f"Color palette STRICTLY: {accent} as primary accent, dark background. "
        f"Do NOT use colors outside this palette: {', '.join(colores_hex)}. "
        f"No text, no letters, no words, no people, no faces, no hands. "
        f"Clean, modern, professional. High quality texture."
    )

    try:
        result = generar_imagen(
            prompt=prompt,
            size=size_key,
            style="vivid",
            custom_api_key=leonardo_api_key,
            tipo="placa",
        )
        url = result.get("url")
        if not url:
            logger.warning("[placa] Leonardo no devolvió URL")
            return None

        img = _download_image(url)
        img = img.resize((width, height), Image.LANCZOS)
        dark_overlay = Image.new("RGB", (width, height), (0, 0, 0))
        img = Image.blend(img, dark_overlay, alpha=0.35)
        logger.info("[placa] fondo Leonardo descargado y procesado")
        return img

    except (LeonardoError, requests.RequestException) as e:
        logger.warning("[placa] fallback a fondo sólido — %s", e)
        return None


def _hex_to_rgb(h: str) -> tuple:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _resolve_colors(colores_hex: list) -> dict:
    """Resuelve colores de la paleta de marca para cada elemento de la placa."""
    colors = colores_hex or [_ACCENT_COLOR]

    text_color = colors[0]  # primer color = texto principal
    line_color = colors[1] if len(colors) > 1 else colors[0]  # segundo = línea decorativa

    # Color más oscuro de la paleta para fondo sólido (fallback)
    darkest = _BG_COLOR
    min_lum = 999
    for c in colors:
        rgb = _hex_to_rgb(c)
        lum = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]
        if lum < min_lum:
            min_lum = lum
            darkest = c

    return {
        "text": _hex_to_rgb(text_color),
        "line": _hex_to_rgb(line_color),
        "bg": _hex_to_rgb(darkest),
        "logo": _hex_to_rgb(_LOGO_COLOR),
    }


def _overlay_text(
    img: Image.Image,
    texto: str,
    colores_hex: list,
    width: int,
    height: int,
) -> Image.Image:
    """Superpone texto centrado con sombra sobre la imagen usando colores de marca."""
    draw = ImageDraw.Draw(img)
    palette = _resolve_colors(colores_hex)

    # Auto-size font based on text length
    max_chars_per_line = 20
    if len(texto) <= 30:
        font_size = int(width * 0.08)
        max_chars_per_line = 15
    elif len(texto) <= 60:
        font_size = int(width * 0.06)
        max_chars_per_line = 20
    else:
        font_size = int(width * 0.045)
        max_chars_per_line = 28

    font_main = _get_font(font_size)
    font_logo = _get_font(int(width * 0.025))

    lines = textwrap.wrap(texto, width=max_chars_per_line)
    if not lines:
        lines = [texto]

    line_height = font_size * 1.3
    total_text_h = len(lines) * line_height
    start_y = (height - total_text_h) / 2 - height * 0.03

    shadow_offset = max(2, font_size // 20)

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font_main)
        tw = bbox[2] - bbox[0]
        x = (width - tw) / 2
        y = start_y + i * line_height

        # Shadow
        draw.text((x + shadow_offset, y + shadow_offset), line, fill=(0, 0, 0), font=font_main)
        draw.text((x - 1, y - 1), line, fill=(0, 0, 0, 180), font=font_main)
        # Texto principal — primer color de la paleta
        draw.text((x, y), line, fill=palette["text"], font=font_main)

    # Línea decorativa — segundo color de la paleta
    deco_y = start_y + total_text_h + height * 0.04
    line_w = min(width * 0.3, 300)
    line_x = (width - line_w) / 2
    draw.rectangle(
        [line_x, deco_y, line_x + line_w, deco_y + 4],
        fill=palette["line"],
    )

    # NEXO logo
    logo_text = "NEXO"
    logo_bbox = draw.textbbox((0, 0), logo_text, font=font_logo)
    logo_w = logo_bbox[2] - logo_bbox[0]
    draw.text(
        (width - logo_w - width * 0.04, height - height * 0.06),
        logo_text, fill=palette["logo"], font=font_logo,
    )

    return img


def generar_placa(
    texto: str,
    colores_hex: list = None,
    width: int = 1080,
    height: int = 1080,
    leonardo_api_key: str = None,
    size_key: str = "1024x1024",
) -> bytes:
    """
    Genera una placa PNG con texto centrado.

    Si hay leonardo_api_key, genera fondo abstracto con Leonardo AI.
    Si no, usa fondo sólido con el color más oscuro de la paleta.

    Args:
        texto: texto principal a mostrar
        colores_hex: lista de hex codes del perfil de marca
        width: ancho en px
        height: alto en px
        leonardo_api_key: API key de Leonardo (None = fondo sólido)
        size_key: clave de tamaño para Leonardo ("1024x1024", etc.)

    Returns:
        bytes del PNG generado
    """
    hex_list = colores_hex or [_ACCENT_COLOR]

    bg_img = None
    if leonardo_api_key:
        bg_img = _generate_leonardo_background(
            texto, hex_list, width, height, leonardo_api_key, size_key,
        )

    if bg_img is None:
        palette = _resolve_colors(hex_list)
        bg_img = Image.new("RGB", (width, height), palette["bg"])

    final = _overlay_text(bg_img, texto, hex_list, width, height)

    buf = io.BytesIO()
    final.save(buf, format="PNG", quality=95)
    buf.seek(0)

    source = "leonardo+pillow" if leonardo_api_key else "pillow"
    logger.info("[placa] generada — %dx%d, source=%s", width, height, source)
    return buf.getvalue()
