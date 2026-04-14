"""Cliente Semrush API para investigación de keywords y competidores."""
from __future__ import annotations

import logging
from typing import Optional

import requests

from config.settings import get_settings

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.semrush.com"


def _is_mock() -> bool:
    """Retorna True si no hay API key válida de Semrush."""
    key = get_settings().SEMRUSH_API_KEY
    return not key or key == "mock"


def buscar_keywords(query: str, database: str = "ar") -> list:
    """Busca keywords relacionadas con volumen, dificultad e intención."""
    if _is_mock():
        logger.debug("[semrush] buscar_keywords — modo mock")
        return [
            {"keyword": f"{query}", "volumen_mensual": 2400, "dificultad": 45, "intencion": "transaccional"},
            {"keyword": f"{query} online", "volumen_mensual": 1200, "dificultad": 38, "intencion": "transaccional"},
            {"keyword": f"mejor {query}", "volumen_mensual": 880, "dificultad": 52, "intencion": "comercial"},
            {"keyword": f"{query} precio", "volumen_mensual": 720, "dificultad": 30, "intencion": "comercial"},
            {"keyword": f"qué es {query}", "volumen_mensual": 590, "dificultad": 22, "intencion": "informacional"},
        ]

    r = requests.get(
        f"{_BASE_URL}/",
        params={"type": "phrase_related", "key": get_settings().SEMRUSH_API_KEY,
                "phrase": query, "database": database, "export_columns": "Ph,Nq,Kd"},
        timeout=30,
    )
    r.raise_for_status()
    return _parse_semrush_response(r.text)


def analizar_competidor(dominio: str, marca_dominio: str) -> dict:
    """Identifica keywords del competidor que la marca no rankea."""
    if _is_mock():
        logger.debug("[semrush] analizar_competidor — modo mock")
        return {
            "dominio": dominio, "keywords_exclusivas": [
                {"keyword": f"servicio {dominio.split('.')[0]}", "volumen_mensual": 1100, "posicion": 3},
                {"keyword": f"{dominio.split('.')[0]} alternativa", "volumen_mensual": 650, "posicion": 5},
            ], "total_keywords_competidor": 145, "mock": True,
        }

    r = requests.get(
        f"{_BASE_URL}/",
        params={"type": "domain_domains", "key": get_settings().SEMRUSH_API_KEY,
                "domains": f"{marca_dominio}|or|{dominio}|or", "export_columns": "Ph,Nq,Po"},
        timeout=30,
    )
    r.raise_for_status()
    return {"dominio": dominio, "keywords_exclusivas": _parse_semrush_response(r.text), "mock": False}


def obtener_posiciones(dominio: str, keywords: list) -> list:
    """Retorna posición actual por keyword para el dominio dado."""
    if _is_mock():
        logger.debug("[semrush] obtener_posiciones — modo mock")
        return [{"keyword": kw, "posicion": (i + 1) * 3, "mock": True} for i, kw in enumerate(keywords)]

    r = requests.get(
        f"{_BASE_URL}/",
        params={"type": "domain_organic", "key": get_settings().SEMRUSH_API_KEY,
                "domain": dominio, "export_columns": "Ph,Po"},
        timeout=30,
    )
    r.raise_for_status()
    return _parse_semrush_response(r.text)


def _parse_semrush_response(text: str) -> list:
    """Parsea respuesta CSV de Semrush a lista de dicts."""
    lines = text.strip().split("\n")
    if len(lines) < 2:
        return []
    headers = [h.strip() for h in lines[0].split(";")]
    results = []
    for line in lines[1:]:
        values = line.split(";")
        results.append(dict(zip(headers, values)))
    return results
