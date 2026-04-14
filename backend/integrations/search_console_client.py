"""Cliente Google Search Console API para métricas orgánicas."""
from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def _is_mock(credentials: Optional[str] = None) -> bool:
    """Retorna True si no hay credenciales de Search Console."""
    return not credentials or credentials == "mock"


def obtener_metricas(site_url: str, fecha_inicio: str, fecha_fin: str,
                     credentials: Optional[str] = None) -> dict:
    """Retorna clicks, impresiones, CTR por keyword desde Search Console."""
    if _is_mock(credentials):
        logger.debug("[search_console] obtener_metricas — modo mock")
        return {
            "site_url": site_url, "periodo": f"{fecha_inicio} a {fecha_fin}",
            "keywords": [
                {"keyword": "ejemplo keyword", "clicks": 120, "impresiones": 3400, "ctr": 0.0353, "posicion": 8.2},
                {"keyword": "otro término", "clicks": 85, "impresiones": 2100, "ctr": 0.0405, "posicion": 12.5},
            ],
            "mock": True,
        }

    # Producción: usar google-auth y googleapiclient
    # from googleapiclient.discovery import build
    raise NotImplementedError("Search Console API requiere configuración OAuth de producción")


def obtener_posiciones(site_url: str, keywords: list,
                       credentials: Optional[str] = None) -> list:
    """Retorna posición actual por keyword desde Search Console."""
    if _is_mock(credentials):
        logger.debug("[search_console] obtener_posiciones — modo mock")
        return [
            {"keyword": kw, "posicion": (i + 1) * 4 + 2, "clicks": 50, "impresiones": 1200, "mock": True}
            for i, kw in enumerate(keywords)
        ]

    raise NotImplementedError("Search Console API requiere configuración OAuth de producción")
