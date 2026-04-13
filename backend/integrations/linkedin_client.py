"""
Cliente LinkedIn API para publicaciones orgánicas.

Si no hay credenciales reales retorna mock en lugar de explotar.
En producción reemplazar con llamadas reales a api.linkedin.com.
"""

import logging
import time
from typing import Optional

import requests

logger = logging.getLogger(__name__)

_API_URL = "https://api.linkedin.com/v2"


def _is_mock(access_token: Optional[str]) -> bool:
    return not access_token or access_token.startswith("mock")


def _mock_response() -> dict:
    post_id = f"mock-li-{int(time.time())}"
    return {
        "post_id_externo": post_id,
        "url_publicacion": f"https://www.linkedin.com/feed/update/{post_id}/",
        "mock": True,
    }


def publicar_linkedin(
    access_token: str,
    person_id: str,
    copy: str,
    imagen_url: Optional[str] = None,
) -> dict:
    """
    Publica en LinkedIn como persona o company page via UGC Posts API.

    Args:
        access_token: Token OAuth2 de LinkedIn
        person_id: URN del autor (ej: urn:li:person:ABC123 o urn:li:organization:123)
        copy: Texto del post
        imagen_url: URL de imagen (ignorado en esta versión MVP)

    Returns:
        Dict con post_id_externo, url_publicacion y mock=True si es simulado
    """
    if _is_mock(access_token):
        logger.debug("[linkedin_client] publicar_linkedin — modo mock")
        return _mock_response()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }
    payload = {
        "author": person_id,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": copy},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }

    r = requests.post(f"{_API_URL}/ugcPosts", json=payload, headers=headers, timeout=30)
    r.raise_for_status()
    post_id = r.headers.get("x-restli-id", "")

    return {
        "post_id_externo": post_id,
        "url_publicacion": f"https://www.linkedin.com/feed/update/{post_id}/",
        "mock": False,
    }


def obtener_metricas_post(access_token: str, post_id: str) -> dict:
    """
    Obtiene likes y comentarios de un post de LinkedIn via Social Actions API.

    Returns:
        Dict con likes, comentarios, alcance — valores 0 si es mock
    """
    if _is_mock(access_token) or post_id.startswith("mock"):
        return {"likes": 0, "comentarios": 0, "alcance": 0, "mock": True}

    headers = {"Authorization": f"Bearer {access_token}"}
    r = requests.get(
        f"{_API_URL}/socialActions/{post_id}",
        headers=headers,
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()

    return {
        "likes": data.get("likesSummary", {}).get("totalLikes", 0),
        "comentarios": data.get("commentsSummary", {}).get("totalFirstLevelComments", 0),
        "alcance": 0,
        "mock": False,
    }
