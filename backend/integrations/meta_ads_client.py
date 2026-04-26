"""Cliente Meta Ads API para gestión de campañas publicitarias."""

from __future__ import annotations

import logging
import time
from typing import Optional

import requests

logger = logging.getLogger(__name__)

_GRAPH_URL = "https://graph.facebook.com/v19.0"


def _is_mock(token: Optional[str]) -> bool:
    return not token or token.startswith("mock")


def crear_campana(access_token: str, ad_account_id: str, data: dict) -> dict:
    """Crea una campaña en Meta Ads. Mock si token no es real."""
    if _is_mock(access_token):
        logger.debug("[meta_ads] crear_campana — modo mock")
        cid = f"mock-camp-{int(time.time())}"
        return {"campaign_id_externo": cid, "mock": True}

    r = requests.post(
        f"{_GRAPH_URL}/act_{ad_account_id}/campaigns",
        json={
            "name": data["nombre"],
            "objective": data.get("objetivo", "OUTCOME_TRAFFIC"),
            "status": "PAUSED",
            "daily_budget": int(float(data["presupuesto_diario"]) * 100),
            "access_token": access_token,
        },
        timeout=30,
    )
    r.raise_for_status()
    return {"campaign_id_externo": r.json()["id"], "mock": False}


def pausar_campana(access_token: str, campaign_id: str) -> dict:
    """Pausa una campaña en Meta Ads."""
    if _is_mock(access_token):
        return {"status": "PAUSED", "mock": True}

    r = requests.post(
        f"{_GRAPH_URL}/{campaign_id}",
        json={"status": "PAUSED", "access_token": access_token},
        timeout=30,
    )
    r.raise_for_status()
    return {"status": "PAUSED", "mock": False}


def activar_campana(access_token: str, campaign_id: str) -> dict:
    """Activa una campaña en Meta Ads."""
    if _is_mock(access_token):
        return {"status": "ACTIVE", "mock": True}

    r = requests.post(
        f"{_GRAPH_URL}/{campaign_id}",
        json={"status": "ACTIVE", "access_token": access_token},
        timeout=30,
    )
    r.raise_for_status()
    return {"status": "ACTIVE", "mock": False}


def obtener_metricas(access_token: str, campaign_id: str, fecha: str) -> dict:
    """Obtiene métricas de una campaña para una fecha dada."""
    if _is_mock(access_token) or campaign_id.startswith("mock"):
        return {
            "impresiones": 0,
            "clicks": 0,
            "conversiones": 0,
            "gasto": 0.0,
            "mock": True,
        }

    r = requests.get(
        f"{_GRAPH_URL}/{campaign_id}/insights",
        params={
            "fields": "impressions,clicks,actions,spend",
            "time_range": f'{{"since":"{fecha}","until":"{fecha}"}}',
            "access_token": access_token,
        },
        timeout=30,
    )
    r.raise_for_status()
    data = r.json().get("data", [{}])[0]
    conversiones = 0
    for a in data.get("actions", []):
        if a["action_type"] == "offsite_conversion":
            conversiones = int(a["value"])
    return {
        "impresiones": int(data.get("impressions", 0)),
        "clicks": int(data.get("clicks", 0)),
        "conversiones": conversiones,
        "gasto": float(data.get("spend", 0)),
        "mock": False,
    }
