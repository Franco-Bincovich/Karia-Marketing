"""Funciones Claude para agentes — traducción visual de conceptos."""

import logging
import re

from integrations.claude.base import _get_client

logger = logging.getLogger(__name__)


def traducir_concepto_a_prompt_visual(descripcion_usuario: str, perfil_marca: dict, formato: str = "post") -> str:
    """Traduce una descripción conceptual a un prompt visual para Leonardo."""
    client = _get_client()

    colores_raw = perfil_marca.get("colores_marca", [])
    colores_str = " ".join(colores_raw) if isinstance(colores_raw, list) else str(colores_raw or "")
    hex_codes = re.findall(r"#[0-9A-Fa-f]{6}", colores_str)
    palette = hex_codes if hex_codes else ["#09090B", "#FF6B00", "#FFFFFF"]

    estetica = perfil_marca.get("estetica_visual", "") or ""
    industria = perfil_marca.get("industria", "") or "marketing"
    audiencia = perfil_marca.get("audiencia", "") or "small business owners"

    system = (
        "Sos un art director de una agencia de marketing. Traducís conceptos "
        "a descripciones visuales en inglés para IA generativa.\n\n"
        "REGLAS:\n"
        "1. NUNCA incluyas texto literal del cliente en la imagen. Traducí el CONCEPTO a una ESCENA.\n"
        "2. Priorizá escenas realistas: fotografía editorial, personas, objetos, oficinas.\n"
        "3. Paleta de marca = ATMÓSFERA E ILUMINACIÓN, no monocromía.\n"
        "4. SOLO el prompt visual final en inglés. Máximo 100 palabras.\n"
        "5. Terminá con: 'professional marketing photography, cinematic lighting, "
        "shot on 35mm, high detail, natural composition'."
    )

    user = (
        f"CONCEPTO: {descripcion_usuario}\n\n"
        f"MARCA: Industria: {industria} | Audiencia: {audiencia}\n"
        f"Paleta: {', '.join(palette[:4])} | Estética: {estetica[:200]}\n"
        f"Formato: {formato}\n\nDevolvé el prompt visual en inglés."
    )

    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=300,
        system=system,
        messages=[{"role": "user", "content": user}],
    )

    text_blocks = [b for b in message.content if b.type == "text"]
    if not text_blocks:
        return f"Professional marketing photograph: {descripcion_usuario}. Cinematic lighting, 35mm."

    visual_prompt = text_blocks[0].text.strip()
    return visual_prompt.strip("`").strip('"').strip("'")
