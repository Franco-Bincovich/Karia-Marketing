"""
Cliente Meta Graph API para publicaciones en Instagram y Facebook.

Si no hay credenciales reales retorna una respuesta mock en lugar de explotar.
En producción reemplazar los bloques mock con llamadas reales a graph.facebook.com.
"""

import logging
import time
from typing import Optional

import requests

logger = logging.getLogger(__name__)

_GRAPH_URL = "https://graph.facebook.com/v19.0"


def _is_mock(access_token: Optional[str]) -> bool:
    return not access_token or access_token.startswith("mock")


def _mock_response(red_social: str) -> dict:
    post_id = f"mock-{int(time.time())}"
    return {
        "post_id_externo": post_id,
        "url_publicacion": f"https://{red_social}.com/p/{post_id}",
        "mock": True,
    }


def publicar_instagram(
    access_token: str,
    account_id: str,
    copy: str,
    imagen_url: Optional[str] = None,
) -> dict:
    """
    Publica en Instagram via Meta Graph API (Container → Publish flow).

    Args:
        access_token: Token de acceso de la cuenta
        account_id: Instagram Business Account ID
        copy: Texto del post
        imagen_url: URL pública de la imagen (opcional)

    Returns:
        Dict con post_id_externo, url_publicacion y mock=True si es simulado
    """
    if _is_mock(access_token):
        logger.debug("[meta_client] publicar_instagram — modo mock")
        return _mock_response("instagram")

    # 1. Crear container de media
    container_payload = {"caption": copy, "access_token": access_token}
    if imagen_url:
        container_payload["image_url"] = imagen_url

    r = requests.post(f"{_GRAPH_URL}/{account_id}/media", json=container_payload, timeout=30)
    r.raise_for_status()
    container_id = r.json()["id"]

    # 2. Publicar el container
    r2 = requests.post(
        f"{_GRAPH_URL}/{account_id}/media_publish",
        json={"creation_id": container_id, "access_token": access_token},
        timeout=30,
    )
    r2.raise_for_status()
    post_id = r2.json()["id"]

    return {"post_id_externo": post_id, "url_publicacion": f"https://www.instagram.com/p/{post_id}/", "mock": False}


def publicar_facebook(
    access_token: str,
    page_id: str,
    copy: str,
    imagen_url: Optional[str] = None,
) -> dict:
    """
    Publica en una Página de Facebook via Graph API.

    Returns:
        Dict con post_id_externo, url_publicacion y mock=True si es simulado
    """
    if _is_mock(access_token):
        logger.debug("[meta_client] publicar_facebook — modo mock")
        return _mock_response("facebook")

    payload = {"message": copy, "access_token": access_token}
    endpoint = f"{_GRAPH_URL}/{page_id}/photos" if imagen_url else f"{_GRAPH_URL}/{page_id}/feed"
    if imagen_url:
        payload["url"] = imagen_url

    r = requests.post(endpoint, json=payload, timeout=30)
    r.raise_for_status()
    post_id = r.json().get("id", r.json().get("post_id"))

    return {"post_id_externo": post_id, "url_publicacion": f"https://www.facebook.com/{post_id}", "mock": False}


def obtener_metricas_post(access_token: str, post_id: str) -> dict:
    """
    Obtiene likes, comentarios y alcance de un post de Instagram/Facebook.

    Returns:
        Dict con likes, comentarios, alcance — valores 0 si es mock
    """
    if _is_mock(access_token) or post_id.startswith("mock"):
        return {"likes": 0, "comentarios": 0, "alcance": 0, "mock": True}

    r = requests.get(
        f"{_GRAPH_URL}/{post_id}/insights",
        params={"metric": "impressions,reach,likes", "access_token": access_token},
        timeout=30,
    )
    r.raise_for_status()
    data = {item["name"]: item["values"][0]["value"] for item in r.json().get("data", [])}
    return {"likes": data.get("likes", 0), "comentarios": 0, "alcance": data.get("reach", 0), "mock": False}
