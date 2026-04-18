"""Servicio de gestión de API keys — panel de configuración superadmin."""

import logging
from uuid import UUID

from sqlalchemy.orm import Session

from config.settings import get_settings
from middleware.error_handler import AppError
from models.api_keys_models import ApiKeyConfigMkt
from utils.security import encrypt_token

logger = logging.getLogger(__name__)

SERVICIOS = ["anthropic", "openai", "canva", "zernio"]
ENV_SERVICIOS = {"anthropic", "zernio"}  # Configurados via .env, solo informativos


def _env_configurada(servicio: str) -> bool:
    """Chequea si el servicio tiene key configurada en .env."""
    settings = get_settings()
    if servicio == "anthropic":
        return bool(settings.ANTHROPIC_API_KEY)
    if servicio == "zernio":
        return bool(settings.ZERNIO_API_KEY)
    if servicio == "openai":
        return bool(settings.OPENAI_API_KEY)
    return False


def listar(db: Session, cliente_id: UUID) -> list[dict]:
    """Lista todos los servicios con su estado. Nunca devuelve el valor de la key."""
    db_keys = db.query(ApiKeyConfigMkt).filter(ApiKeyConfigMkt.cliente_id == cliente_id).all()
    db_map = {k.servicio: k for k in db_keys}

    resultado = []
    for servicio in SERVICIOS:
        is_env = servicio in ENV_SERVICIOS
        db_entry = db_map.get(servicio)

        if is_env:
            resultado.append({
                "servicio": servicio,
                "configurada": _env_configurada(servicio),
                "origen": "env",
                "editable": False,
                "updated_at": None,
            })
        else:
            resultado.append({
                "servicio": servicio,
                "configurada": db_entry.configurada if db_entry else _env_configurada(servicio),
                "origen": "db" if db_entry and db_entry.configurada else ("env" if _env_configurada(servicio) else "ninguno"),
                "editable": True,
                "updated_at": db_entry.updated_at.isoformat() if db_entry and db_entry.updated_at else None,
            })

    return resultado


def guardar(db: Session, cliente_id: UUID, servicio: str, api_key: str) -> dict:
    """Guarda o actualiza una API key encriptada."""
    if servicio not in SERVICIOS:
        raise AppError(f"Servicio '{servicio}' no reconocido", "INVALID_SERVICE", 400)
    if servicio in ENV_SERVICIOS:
        raise AppError(f"La key de {servicio} se gestiona vía sistema y no puede modificarse desde la UI", "ENV_MANAGED", 403)

    encrypted = encrypt_token(api_key)

    obj = db.query(ApiKeyConfigMkt).filter(
        ApiKeyConfigMkt.cliente_id == cliente_id, ApiKeyConfigMkt.servicio == servicio,
    ).first()

    if obj:
        obj.api_key_encrypted = encrypted
        obj.configurada = True
    else:
        obj = ApiKeyConfigMkt(cliente_id=cliente_id, servicio=servicio, api_key_encrypted=encrypted, configurada=True)
        db.add(obj)

    db.flush()
    db.commit()
    logger.info("[api_keys] guardada key para %s — cliente=%s", servicio, cliente_id)
    return {"servicio": servicio, "configurada": True, "origen": "db", "editable": True}


def eliminar(db: Session, cliente_id: UUID, servicio: str) -> dict:
    """Elimina una API key."""
    if servicio in ENV_SERVICIOS:
        raise AppError(f"La key de {servicio} se gestiona vía sistema", "ENV_MANAGED", 403)

    obj = db.query(ApiKeyConfigMkt).filter(
        ApiKeyConfigMkt.cliente_id == cliente_id, ApiKeyConfigMkt.servicio == servicio,
    ).first()

    if obj:
        db.delete(obj)
        db.commit()

    return {"servicio": servicio, "configurada": False}
