"""
Servicio centralizado para publicación en redes sociales vía Zernio.

Maneja: OAuth, publicación inmediata, programación, límites por plan.
"""

import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from integrations.zernio_client import (
    ZernioError,
    exchange_oauth_token,
    get_oauth_url,
    publish_now,
    schedule_post,
)
from middleware.audit import registrar_auditoria
from middleware.error_handler import AppError
from repositories import cuentas_sociales_repository as cuentas_repo
from repositories import publicaciones_repository as pub_repo
from utils.security import encrypt_token

logger = logging.getLogger(__name__)

PLAN_LIMITS = {
    "Basic": {"redes": ["instagram"], "posts_mes": 30},
    "Premium": {"redes": ["instagram", "facebook"], "posts_mes": None},  # None = sin límite
}


def _get_plan_limits(db: Session, marca_id: UUID) -> dict:
    """Obtiene los límites del plan del cliente que posee la marca."""
    from models.cliente_models import ClienteMkt, MarcaMkt
    marca = db.query(MarcaMkt).filter(MarcaMkt.id == marca_id).first()
    if not marca:
        raise AppError("Marca no encontrada", "MARCA_NOT_FOUND", 404)
    cliente = db.query(ClienteMkt).filter(ClienteMkt.id == marca.cliente_id).first()
    if not cliente:
        raise AppError("Cliente no encontrado", "CLIENT_NOT_FOUND", 404)
    return PLAN_LIMITS.get(cliente.plan, PLAN_LIMITS["Basic"])


def _check_red_permitida(limits: dict, red_social: str):
    """Valida que la red social esté disponible en el plan."""
    if red_social not in limits["redes"]:
        redes = ", ".join(limits["redes"])
        raise AppError(
            f"Tu plan solo permite publicar en: {redes}. Upgrade a Premium para más redes.",
            "PLAN_LIMIT_RED", 403,
        )


def _check_limite_posts(db: Session, marca_id: UUID, limits: dict):
    """Valida que no se exceda el límite mensual de posts."""
    if limits["posts_mes"] is None:
        return
    conteo = pub_repo.contar_mes_actual(db, marca_id)
    if conteo >= limits["posts_mes"]:
        raise AppError(
            f"Alcanzaste el límite de {limits['posts_mes']} publicaciones/mes de tu plan. Upgrade a Premium.",
            "PLAN_LIMIT_POSTS", 403,
        )


# --- OAuth ---

def iniciar_oauth(db: Session, marca_id: UUID, platform: str, callback_url: str) -> dict:
    """Genera la URL de OAuth para conectar una cuenta social vía Zernio."""
    limits = _get_plan_limits(db, marca_id)
    _check_red_permitida(limits, platform)

    try:
        result = get_oauth_url(platform, callback_url, state=str(marca_id))
        return {"auth_url": result.get("auth_url"), "platform": platform}
    except ZernioError as e:
        raise AppError(f"Error al conectar con Zernio: {e.message}", "ZERNIO_ERROR", e.status_code)


def completar_oauth(db: Session, marca_id: UUID, code: str, state: str, actor_id: UUID) -> dict:
    """Intercambia el code de OAuth por tokens y guarda la cuenta conectada."""
    try:
        token_data = exchange_oauth_token(code, state)
    except ZernioError as e:
        raise AppError(f"Error al obtener tokens: {e.message}", "ZERNIO_OAUTH_ERROR", e.status_code)

    encrypted = encrypt_token(token_data["access_token"])
    expires_at = None
    if token_data.get("expires_at"):
        expires_at = datetime.fromisoformat(token_data["expires_at"])

    cuenta = cuentas_repo.crear_o_actualizar(db, {
        "marca_id": marca_id,
        "red_social": token_data.get("platform", state),
        "nombre_cuenta": token_data.get("account_name", ""),
        "account_id_externo": token_data.get("account_id"),
        "access_token_encrypted": encrypted,
        "token_expires_at": expires_at,
        "activa": True,
    })

    registrar_auditoria(db, "conectar_cuenta_social", "social", usuario_id=actor_id)
    db.commit()
    return cuenta


# --- Publicación ---

def publicar_ahora(
    db: Session,
    marca_id: UUID,
    red_social: str,
    copy: str,
    imagen_url: Optional[str] = None,
    contenido_id: Optional[UUID] = None,
    actor_id: Optional[UUID] = None,
) -> dict:
    """Publica un post de forma inmediata a través de Zernio."""
    limits = _get_plan_limits(db, marca_id)
    _check_red_permitida(limits, red_social)
    _check_limite_posts(db, marca_id, limits)

    cuenta = cuentas_repo.obtener_por_red(db, marca_id, red_social)
    if not cuenta:
        raise AppError(
            f"No hay cuenta de {red_social} conectada. Conectá una primero.",
            "NO_ACCOUNT", 400,
        )

    pub_data = {
        "marca_id": marca_id,
        "red_social": red_social,
        "copy_publicado": copy,
        "imagen_url": imagen_url,
        "contenido_id": contenido_id,
        "estado": "publicando",
    }
    pub = pub_repo.crear(db, pub_data)
    db.flush()

    try:
        result = publish_now(
            account_id=cuenta.account_id_externo,
            text=copy,
            image_url=imagen_url,
        )
        pub = pub_repo.actualizar_estado(db, UUID(pub["id"]), "publicado")
        pub_obj = db.query(pub_repo.PublicacionesMkt).filter(
            pub_repo.PublicacionesMkt.id == UUID(pub["id"])
        ).first()
        if pub_obj:
            pub_obj.post_id_externo = result.get("external_post_id")
            pub_obj.url_publicacion = result.get("url")
            pub_obj.zernio_post_id = result.get("id")
            db.flush()
            pub = pub_repo._s(pub_obj)
    except ZernioError as e:
        pub_repo.actualizar_estado(db, UUID(pub["id"]), "fallido", error=e.message)
        db.commit()
        raise AppError(f"Error al publicar: {e.message}", "ZERNIO_PUBLISH_ERROR", e.status_code)

    if actor_id:
        registrar_auditoria(db, "publicar_post", "social", usuario_id=actor_id)
    db.commit()
    return pub


def programar_publicacion(
    db: Session,
    marca_id: UUID,
    red_social: str,
    copy: str,
    programado_para: datetime,
    imagen_url: Optional[str] = None,
    contenido_id: Optional[UUID] = None,
    actor_id: Optional[UUID] = None,
) -> dict:
    """Programa un post para fecha futura a través de Zernio."""
    limits = _get_plan_limits(db, marca_id)
    _check_red_permitida(limits, red_social)
    _check_limite_posts(db, marca_id, limits)

    if programado_para <= datetime.now(timezone.utc):
        raise AppError("La fecha de programación debe ser futura", "INVALID_SCHEDULE", 400)

    cuenta = cuentas_repo.obtener_por_red(db, marca_id, red_social)
    if not cuenta:
        raise AppError(
            f"No hay cuenta de {red_social} conectada. Conectá una primero.",
            "NO_ACCOUNT", 400,
        )

    pub_data = {
        "marca_id": marca_id,
        "red_social": red_social,
        "copy_publicado": copy,
        "imagen_url": imagen_url,
        "contenido_id": contenido_id,
        "estado": "programado",
        "programado_para": programado_para,
    }
    pub = pub_repo.crear(db, pub_data)
    db.flush()

    try:
        result = schedule_post(
            account_id=cuenta.account_id_externo,
            text=copy,
            scheduled_at=programado_para,
            image_url=imagen_url,
        )
        pub_obj = db.query(pub_repo.PublicacionesMkt).filter(
            pub_repo.PublicacionesMkt.id == UUID(pub["id"])
        ).first()
        if pub_obj:
            pub_obj.zernio_post_id = result.get("id")
            db.flush()
            pub = pub_repo._s(pub_obj)
    except ZernioError as e:
        pub_repo.actualizar_estado(db, UUID(pub["id"]), "fallido", error=e.message)
        db.commit()
        raise AppError(f"Error al programar: {e.message}", "ZERNIO_SCHEDULE_ERROR", e.status_code)

    if actor_id:
        registrar_auditoria(db, "programar_post", "social", usuario_id=actor_id)
    db.commit()
    return pub


# --- Webhook ---

def procesar_webhook(payload: dict) -> dict:
    """
    Procesa webhook de Zernio para confirmar publicación.
    Placeholder — implementar cuando Zernio envíe callbacks.
    """
    # TODO: Implementar procesamiento de webhook
    # event_type = payload.get("event")  # "post.published", "post.failed"
    # zernio_post_id = payload.get("post_id")
    # Buscar publicación por zernio_post_id y actualizar estado
    logger.info("[zernio_webhook] Payload recibido: %s", payload)
    return {"received": True}
