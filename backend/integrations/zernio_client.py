"""
Cliente HTTP para la API de Zernio — publicación en redes sociales.

Endpoints principales:
- OAuth: iniciar conexión de cuenta social
- Publish: publicar post inmediatamente
- Schedule: programar post para fecha futura
- Accounts: listar cuentas conectadas
- Webhooks: confirmación de publicación (callback)
"""

import json
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
    Crea un invite link de Zernio para conectar una cuenta social.

    Args:
        platform: "instagram" o "facebook"
        callback_url: URL de callback para completar OAuth
        state: string opaco para CSRF (ej. marca_id)

    Returns:
        {"auth_url": "https://...", "state": "..."}
    """
    return _request("POST", "/platform-invites", {
        "platform": platform,
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


# --- Helpers de media ---

def _upload_media(image_url: str) -> Optional[str]:
    """Sube una imagen a Zernio Storage y retorna la URL de Zernio."""
    try:
        # 1. Get upload token
        token_data = _request("POST", "/media/upload-token", {})
        token = token_data["token"]

        # 2. Download image from our URL
        import requests as req
        img_resp = req.get(image_url, timeout=30)
        if img_resp.status_code != 200:
            logger.error("[zernio] No se pudo descargar imagen: %s → HTTP %s", image_url, img_resp.status_code)
            return None

        # 3. Upload to Zernio
        settings = get_settings()
        upload_resp = req.post(
            f"{settings.ZERNIO_BASE_URL}/media/upload?token={token}",
            headers={"Authorization": f"Bearer {settings.ZERNIO_API_KEY}"},
            files={"files": ("image.png", img_resp.content, img_resp.headers.get("Content-Type", "image/png"))},
            timeout=30,
        )
        if upload_resp.status_code != 200:
            logger.error("[zernio] Upload falló: HTTP %s — %s", upload_resp.status_code, upload_resp.text[:200])
            return None

        files = upload_resp.json().get("files", [])
        if not files:
            logger.error("[zernio] Upload OK pero sin files en respuesta")
            return None

        zernio_url = files[0]["url"]
        logger.info("[zernio] Media uploaded: %s → %s", image_url[:60], zernio_url)
        return zernio_url
    except Exception as e:
        logger.error("[zernio] Error uploading media: %s", e)
        return None


# --- Publicación ---

def publish_now(
    account_id: str,
    text: str,
    image_url: Optional[str] = None,
    image_urls: Optional[list] = None,
    platform: str = "instagram",
) -> dict:
    """
    Publica un post de forma inmediata.

    Flow: upload media → single POST with content + media + publishNow.
    """
    # 1. Upload media to Zernio Storage
    zernio_urls = _upload_all_media(image_url, image_urls)

    # 2. Single POST with everything
    payload = {
        "content": text,
        "publishNow": True,
        "platforms": [{"platform": platform, "accountId": account_id}],
    }
    if zernio_urls:
        payload["mediaItems"] = [{"type": "image", "url": u} for u in zernio_urls]
    logger.info("[zernio] publish_now POST payload: %s", json.dumps(payload, default=str))

    result = _request("POST", "/posts", payload)
    post = result.get("post", {})
    return {"id": post.get("_id"), "status": post.get("status", "published"), **post}


def schedule_post(
    account_id: str,
    text: str,
    scheduled_at: datetime,
    image_url: Optional[str] = None,
    image_urls: Optional[list] = None,
    platform: str = "instagram",
) -> dict:
    """
    Programa un post para fecha futura.

    Flow: upload media → single POST with content + media + scheduledFor.
    """
    # 1. Upload media
    zernio_urls = _upload_all_media(image_url, image_urls)

    # 2. Single POST with everything
    payload = {
        "content": text,
        "scheduledFor": scheduled_at.isoformat(),
        "timezone": "America/Argentina/Buenos_Aires",
        "platforms": [{"platform": platform, "accountId": account_id}],
    }
    if zernio_urls:
        payload["mediaItems"] = [{"type": "image", "url": u} for u in zernio_urls]
    logger.info("[zernio] schedule_post POST payload: %s", json.dumps(payload, default=str))

    result = _request("POST", "/posts", payload)
    post = result.get("post", {})
    return {"id": post.get("_id"), "status": post.get("status", "scheduled"), **post}


def _upload_all_media(image_url: Optional[str], image_urls: Optional[list]) -> list:
    """Upload all images to Zernio Storage, return list of Zernio URLs."""
    urls_to_upload = image_urls if (image_urls and len(image_urls) > 1) else ([image_url] if image_url else [])
    zernio_urls = []
    for url in urls_to_upload:
        if url and url.strip():
            z_url = _upload_media(url)
            if z_url:
                zernio_urls.append(z_url)
    return zernio_urls


def get_post_status(zernio_post_id: str) -> dict:
    """Obtiene el estado actual de un post en Zernio."""
    return _request("GET", f"/posts/{zernio_post_id}")
