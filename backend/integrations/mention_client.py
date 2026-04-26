"""Cliente Mention API para social listening."""

from __future__ import annotations

import logging
import time
from typing import Optional

import requests

from config.settings import get_settings

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.mention.net/api"


def _is_mock() -> bool:
    """Retorna True si no hay API key válida de Mention."""
    key = get_settings().MENTION_API_KEY
    return not key or key == "mock"


def buscar_menciones(terminos: list, fecha_desde: Optional[str] = None) -> list:
    """Busca menciones de los términos dados. Mock si no hay credenciales."""
    if _is_mock():
        logger.debug("[mention] buscar_menciones — modo mock")
        return [
            {
                "fuente": "twitter",
                "autor": f"user_{i}",
                "contenido": f"Mencion de {t}",
                "sentimiento": "neutro",
                "alcance_estimado": 500 * (i + 1),
                "url": f"https://twitter.com/user_{i}/status/mock-{int(time.time())}",
            }
            for i, t in enumerate(terminos[:3])
        ]

    headers = {"Authorization": f"Bearer {get_settings().MENTION_API_KEY}"}
    results = []
    for termino in terminos:
        r = requests.get(
            f"{_BASE_URL}/accounts/me/alerts",
            headers=headers,
            params={"query": termino},
            timeout=30,
        )
        r.raise_for_status()
        for item in r.json().get("mentions", []):
            results.append(
                {
                    "fuente": item.get("source", "web"),
                    "autor": item.get("author", ""),
                    "contenido": item.get("title", ""),
                    "sentimiento": "neutro",
                    "alcance_estimado": item.get("reach", 0),
                    "url": item.get("url", ""),
                }
            )
    return results


def obtener_sentimiento(texto: str) -> str:
    """Analiza sentimiento de un texto. Mock retorna 'neutro'."""
    if _is_mock():
        negativas = ["malo", "terrible", "odio", "pésimo", "horrible"]
        positivas = ["genial", "excelente", "increíble", "amor", "mejor"]
        texto_lower = texto.lower()
        if any(p in texto_lower for p in positivas):
            return "positivo"
        if any(n in texto_lower for n in negativas):
            return "negativo"
        return "neutro"
    return "neutro"
