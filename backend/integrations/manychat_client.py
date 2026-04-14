"""Cliente ManyChat API para mensajería automatizada."""
from __future__ import annotations

import logging
import time
from typing import Optional

import requests

from config.settings import get_settings

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.manychat.com/fb"


def _is_mock() -> bool:
    """Retorna True si no hay API key válida de ManyChat."""
    key = get_settings().MANYCHAT_API_KEY
    return not key or key == "mock"


def enviar_mensaje(subscriber_id: str, mensaje: str) -> dict:
    """Envía un mensaje a un suscriptor de ManyChat. Mock si no hay credenciales."""
    if _is_mock():
        logger.debug("[manychat] enviar_mensaje — modo mock")
        return {"status": "sent", "subscriber_id": subscriber_id, "mock": True}

    headers = {"Authorization": f"Bearer {get_settings().MANYCHAT_API_KEY}",
               "Content-Type": "application/json"}
    r = requests.post(
        f"{_BASE_URL}/sending/sendContent",
        headers=headers, json={"subscriber_id": subscriber_id,
                                "data": {"version": "v2", "content": {"messages": [{"type": "text", "text": mensaje}]}}},
        timeout=30,
    )
    r.raise_for_status()
    return {"status": "sent", "subscriber_id": subscriber_id, "mock": False}


def obtener_flujos() -> list:
    """Obtiene los flujos disponibles en ManyChat. Mock si no hay credenciales."""
    if _is_mock():
        logger.debug("[manychat] obtener_flujos — modo mock")
        return [
            {"id": "mock-flow-1", "name": "Bienvenida", "status": "active"},
            {"id": "mock-flow-2", "name": "Consulta comercial", "status": "active"},
        ]

    headers = {"Authorization": f"Bearer {get_settings().MANYCHAT_API_KEY}"}
    r = requests.get(f"{_BASE_URL}/page/getFlows", headers=headers, timeout=30)
    r.raise_for_status()
    return r.json().get("data", [])
