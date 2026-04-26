"""Servicio de generación de briefs SEO para el Agente Contenido."""

from __future__ import annotations

import json
import logging
import re
from uuid import UUID

from sqlalchemy.orm import Session

from integrations.claude_client import _get_client
from middleware.error_handler import AppError
from repositories import briefs_seo_repository as repo

logger = logging.getLogger(__name__)

_SEO_MODEL = "claude-sonnet-4-20250514"

_SYSTEM_PROMPT = (
    "Sos el Agente SEO de KarIA Marketing. Generás briefs de contenido "
    "optimizados para posicionamiento.\n"
    "El brief debe incluir: estructura de encabezados H1/H2/H3, longitud "
    "mínima recomendada, keywords secundarias a incluir, meta title (máx 60 "
    "chars), meta description (máx 155 chars).\n"
    "Respondé SOLO con JSON válido."
)

_JSON_SCHEMA = """{
  "estructura_sugerida": "H1: ...\nH2: ...\nH3: ...",
  "longitud_minima": 1200,
  "intencion_busqueda": "transaccional",
  "competidores_url": "url1, url2",
  "meta_title": "máx 60 chars",
  "meta_description": "máx 155 chars"
}"""


def generar_brief(db: Session, marca_id: UUID, keyword_principal: str, keywords_secundarias: str = "") -> dict:
    """Genera un brief SEO completo usando Claude."""
    prompt = (
        f"Generá un brief SEO para posicionar la keyword: {keyword_principal!r}\n"
        f"Keywords secundarias: {keywords_secundarias or 'sugerí las mejores'}\n"
        f"Respondé con JSON en este formato:\n{_JSON_SCHEMA}"
    )

    try:
        message = _get_client().messages.create(
            model=_SEO_MODEL,
            max_tokens=1024,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        text_blocks = [b for b in message.content if b.type == "text"]
        if not text_blocks:
            raise ValueError("Sin bloques de texto en respuesta")
        resultado = _parse_json(text_blocks[-1].text)
    except Exception as exc:
        logger.warning(f"[briefs_seo_svc] Claude falló, usando fallback: {exc}")
        resultado = _brief_fallback(keyword_principal, keywords_secundarias)

    data = {
        "marca_id": marca_id,
        "keyword_principal": keyword_principal,
        "keywords_secundarias": keywords_secundarias or resultado.get("keywords_secundarias", ""),
        "intencion_busqueda": resultado.get("intencion_busqueda", "informacional"),
        "estructura_sugerida": resultado.get("estructura_sugerida", ""),
        "longitud_minima": int(resultado.get("longitud_minima", 800)),
        "competidores_url": resultado.get("competidores_url", ""),
        "meta_title": resultado.get("meta_title", ""),
        "meta_description": resultado.get("meta_description", ""),
    }
    brief = repo.crear(db, data)
    db.commit()
    return brief


def listar(db: Session, marca_id: UUID) -> list:
    """Lista todos los briefs de una marca."""
    return repo.listar(db, marca_id)


def marcar_usado(db: Session, brief_id: UUID) -> dict:
    """Marca un brief como usado por el Agente Contenido."""
    resultado = repo.marcar_usado(db, brief_id)
    if not resultado:
        raise AppError("Brief no encontrado", "NOT_FOUND", 404)
    db.commit()
    return resultado


def _parse_json(text: str) -> dict:
    """Extrae JSON de la respuesta de Claude."""
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            return json.loads(match.group(0))
        raise ValueError("Respuesta sin JSON válido")


def _brief_fallback(keyword: str, secundarias: str) -> dict:
    """Brief mínimo si Claude no está disponible."""
    return {
        "estructura_sugerida": f"H1: {keyword}\nH2: Beneficios\nH2: Cómo funciona\nH2: FAQ",
        "longitud_minima": 800,
        "intencion_busqueda": "informacional",
        "meta_title": keyword[:57] + "...",
        "meta_description": f"Todo sobre {keyword}. Guía completa.",
    }
