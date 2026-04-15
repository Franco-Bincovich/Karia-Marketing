"""
Cliente HTTP para la API de Zernio — publicación en redes sociales.

Endpoints principales:
- OAuth: iniciar conexión de cuenta social
- Publish: publicar post inmediatamente
- Schedule: programar post para fecha futura
- Accounts: listar cuentas conectadas
- Webhooks: confirmación de publicación (callback)
"""

import logging
from datetime import datetime
from typing import Optional

import requests

from config.settings import get_settings

logger = logging.getLogger(__name__)

_TIMEOUT = 30


def _headers() -> dict:
    settings = get_settings()
    return {
        "Authorization": f"Bearer {settings.ZERNIO_API_KEY}",
        "Content-Type": "application/json",
    }


def _url(path: str) -> str:
    return f"{get_settings().ZERNIO_BASE_URL}{path}"


def _request(method: str, path: str, json: dict = None) -> dict:
    """Request genérico con manejo de errores."""
    try:
        resp = requests.request(
            method, _url(path), headers=_headers(), json=json, timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError as e:
        body = {}
        try:
            body = e.response.json()
        except Exception:
            pass
        logger.error("[zernio] HTTP %s — %s — %s", e.response.status_code, path, body)
        raise ZernioError(
            body.get("message", f"Zernio API error {e.response.status_code}"),
            e.response.status_code,
        )
    except requests.exceptions.ConnectionError:
        logger.error("[zernio] Connection error — %s", path)
        raise ZernioError("No se pudo conectar con Zernio", 503)
    except requests.exceptions.Timeout:
        logger.error("[zernio] Timeout — %s", path)
        raise ZernioError("Timeout conectando con Zernio", 504)


class ZernioError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


# --- OAuth ---

def get_oauth_url(platform: str, callback_url: str, state: str) -> dict:
    """
    Genera URL de OAuth para conectar una cuenta social.

    Args:
        platform: "instagram" o "facebook"
        callback_url: URL de callback para completar OAuth
        state: string opaco para CSRF (ej. marca_id)

    Returns:
        {"auth_url": "https://...", "state": "..."}
    """
    return _request("POST", "/oauth/authorize", {
        "platform": platform,
        "callback_url": callback_url,
        "state": state,
    })


def exchange_oauth_token(code: str, state: str) -> dict:
    """
    Intercambia code de OAuth por tokens de acceso.

    Returns:
        {"access_token": "...", "account_id": "...", "account_name": "...",
         "platform": "...", "expires_at": "..."}
    """
    return _request("POST", "/oauth/token", {
        "code": code,
        "state": state,
    })


# --- Cuentas ---

def list_accounts() -> dict:
    """Lista cuentas conectadas en Zernio."""
    return _request("GET", "/accounts")


# --- Publicación ---

def publish_now(
    account_id: str,
    text: str,
    image_url: Optional[str] = None,
) -> dict:
    """
    Publica un post de forma inmediata.

    Returns:
        {"id": "zernio_post_id", "status": "published",
         "external_post_id": "...", "url": "..."}
    """
    payload = {
        "account_id": account_id,
        "text": text,
    }
    if image_url:
        payload["media"] = [{"type": "image", "url": image_url}]
    return _request("POST", "/posts/publish", payload)


def schedule_post(
    account_id: str,
    text: str,
    scheduled_at: datetime,
    image_url: Optional[str] = None,
) -> dict:
    """
    Programa un post para una fecha futura.

    Args:
        scheduled_at: datetime con timezone (se envía como ISO 8601)

    Returns:
        {"id": "zernio_post_id", "status": "scheduled", "scheduled_at": "..."}
    """
    payload = {
        "account_id": account_id,
        "text": text,
        "scheduled_at": scheduled_at.isoformat(),
    }
    if image_url:
        payload["media"] = [{"type": "image", "url": image_url}]
    return _request("POST", "/posts/schedule", payload)


def get_post_status(zernio_post_id: str) -> dict:
    """Obtiene el estado actual de un post en Zernio."""
    return _request("GET", f"/posts/{zernio_post_id}")
