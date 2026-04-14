"""Cliente Google Ads API para gestión de campañas publicitarias."""
from __future__ import annotations

import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)


def _is_mock(token: Optional[str]) -> bool:
    return not token or token.startswith("mock")


def crear_campana(access_token: str, customer_id: str, data: dict) -> dict:
    """Crea una campaña en Google Ads. Mock si token no es real."""
    if _is_mock(access_token):
        logger.debug("[google_ads] crear_campana — modo mock")
        cid = f"mock-gcamp-{int(time.time())}"
        return {"campaign_id_externo": cid, "mock": True}

    # Producción: usar google-ads-python client library
    # from google.ads.googleads.client import GoogleAdsClient
    raise NotImplementedError("Google Ads API requiere configuración de producción")


def pausar_campana(access_token: str, campaign_id: str) -> dict:
    """Pausa una campaña en Google Ads."""
    if _is_mock(access_token):
        return {"status": "PAUSED", "mock": True}
    raise NotImplementedError("Google Ads API requiere configuración de producción")


def activar_campana(access_token: str, campaign_id: str) -> dict:
    """Activa una campaña en Google Ads."""
    if _is_mock(access_token):
        return {"status": "ACTIVE", "mock": True}
    raise NotImplementedError("Google Ads API requiere configuración de producción")


def obtener_metricas(access_token: str, campaign_id: str, fecha: str) -> dict:
    """Obtiene métricas de una campaña para una fecha dada."""
    if _is_mock(access_token) or campaign_id.startswith("mock"):
        return {
            "impresiones": 0, "clicks": 0, "conversiones": 0,
            "gasto": 0.0, "mock": True,
        }
    raise NotImplementedError("Google Ads API requiere configuración de producción")
