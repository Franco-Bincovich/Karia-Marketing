"""Director de Arte — analiza briefs y toma decisiones creativas."""

import json
import logging
import re

logger = logging.getLogger(__name__)

_SYSTEM = (
    "Sos el Director de Arte de NEXO, una agencia de marketing con IA. "
    "Tu trabajo es analizar briefs de clientes y convertirlos en "
    "instrucciones visuales precisas para el equipo creativo. "
    "Conocés el manual de marca en profundidad. "
    "Tomás decisiones creativas basadas en el objetivo de marketing, "
    "no en preferencias estéticas personales. "
    "Siempre respondés en JSON válido."
)

_MODEL = "claude-sonnet-4-20250514"


def analizar_brief(
    descripcion: str,
    perfil_marca: dict,
    formato: str = "post",
) -> dict:
    """
    Analiza el brief del usuario y produce instrucciones creativas.

    Returns:
        brief_creativo dict con tipo, concepto_visual, textos, mood, etc.
    """
    from integrations.claude_client import _get_client

    palette = _extract_palette(perfil_marca)
    industria = perfil_marca.get("industria", "") or "marketing"
    tono = perfil_marca.get("tono_voz", "") or "profesional"
    nombre = perfil_marca.get("nombre_marca", "") or "la marca"

    user_msg = (
        f"BRIEF DEL CLIENTE: {descripcion}\n\n"
        f"MARCA: {nombre}\n"
        f"INDUSTRIA: {industria}\n"
        f"TONO: {tono}\n"
        f"PALETA: {', '.join(palette[:4])}\n"
        f"FORMATO: {formato}\n\n"
        f"Analizá el brief y devolvé un JSON con esta estructura exacta:\n"
        f"{{\n"
        f'  "tipo": "placa" | "elaborada" | "carrusel",\n'
        f'  "concepto_visual": "descripción concreta de la escena",\n'
        f'  "texto_principal": "texto para overlay (solo si tipo=placa, sino vacío)",\n'
        f'  "texto_secundario": "bajada si aplica (solo si tipo=placa, sino vacío)",\n'
        f'  "mood": "descripción del ambiente/feeling",\n'
        f'  "referencia_formato": "{formato}",\n'
        f'  "razonamiento": "por qué tomaste estas decisiones"\n'
        f"}}\n\n"
        f"REGLAS:\n"
        f"- Si el brief pide texto visible en la imagen → tipo=placa\n"
        f"- Si el brief describe una escena o concepto visual → tipo=elaborada\n"
        f"- Si pide múltiples slides → tipo=carrusel\n"
        f"- concepto_visual debe ser concreto (escena, objetos, personas), nunca abstracto\n"
        f"- SOLO JSON, sin explicación ni markdown"
    )

    try:
        client = _get_client()
        message = client.messages.create(
            model=_MODEL,
            max_tokens=600,
            system=_SYSTEM,
            messages=[{"role": "user", "content": user_msg}],
        )

        text_blocks = [b for b in message.content if b.type == "text"]
        if not text_blocks:
            raise ValueError("Sin respuesta de texto")

        raw = text_blocks[0].text.strip()
        # Limpiar markdown accidental
        if raw.startswith("```"):
            raw = re.sub(r"^```\w*\n?", "", raw)
            raw = re.sub(r"\n?```$", "", raw)

        brief = json.loads(raw)
        logger.info("[director_arte] brief analizado — tipo=%s", brief.get("tipo"))
        return brief

    except Exception as e:
        logger.warning("[director_arte] fallback — error: %s", e)
        return _fallback_brief(descripcion, formato)


def _fallback_brief(descripcion: str, formato: str) -> dict:
    """Brief básico cuando Claude no responde."""
    tiene_texto = any(
        w in descripcion.lower()
        for w in [
            "texto",
            "frase",
            "dice",
            "escribí",
            "título",
            "cartel",
        ]
    )
    return {
        "tipo": "placa" if tiene_texto else "elaborada",
        "concepto_visual": descripcion[:280],
        "texto_principal": descripcion[:80] if tiene_texto else "",
        "texto_secundario": "",
        "mood": "profesional",
        "referencia_formato": formato,
        "razonamiento": "fallback — director_arte no disponible",
    }


def _extract_palette(perfil: dict) -> list:
    raw = perfil.get("colores_marca", [])
    text = " ".join(raw) if isinstance(raw, list) else str(raw or "")
    codes = re.findall(r"#[0-9A-Fa-f]{6}", text)
    return codes if codes else ["#09090B", "#FF6B00", "#FFFFFF"]
