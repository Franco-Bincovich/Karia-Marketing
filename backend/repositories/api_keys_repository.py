"""Repositorio para api_keys_config_mkt — acceso centralizado a API keys."""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from models.api_keys_models import ApiKeyConfigMkt
from utils.security import decrypt_token, encrypt_token

logger = logging.getLogger(__name__)


def obtener_leonardo_key(db: Session, cliente_id: UUID) -> Optional[str]:
    """
    Busca la API key de Leonardo en la tabla api_keys_config_mkt.
    El servicio Leonardo está guardado bajo el nombre 'canva' por
    razones históricas — este repositorio abstrae ese detalle.

    @param db: Sesión de base de datos
    @param cliente_id: UUID del cliente
    @returns: API key desencriptada o None si no existe
    """
    return obtener_key_por_servicio(db, cliente_id, "canva")


def obtener_key_por_servicio(db: Session, cliente_id: UUID, servicio: str) -> Optional[str]:
    """
    Busca cualquier API key por nombre de servicio.

    @param db: Sesión de base de datos
    @param cliente_id: UUID del cliente
    @param servicio: nombre del servicio en la DB
    @returns: API key desencriptada o None si no existe
    """
    obj = (
        db.query(ApiKeyConfigMkt)
        .filter(
            ApiKeyConfigMkt.cliente_id == cliente_id,
            ApiKeyConfigMkt.servicio == servicio,
            ApiKeyConfigMkt.configurada == True,  # noqa: E712
        )
        .first()
    )
    if obj and obj.api_key_encrypted:
        return decrypt_token(obj.api_key_encrypted)
    return None


def guardar_key(db: Session, cliente_id: UUID, servicio: str, api_key: str) -> bool:
    """
    Guarda o actualiza una API key encriptada para un servicio.

    @returns: True si se guardó correctamente
    """
    obj = db.query(ApiKeyConfigMkt).filter(ApiKeyConfigMkt.cliente_id == cliente_id, ApiKeyConfigMkt.servicio == servicio).first()
    if not obj:
        obj = ApiKeyConfigMkt(cliente_id=cliente_id, servicio=servicio)
        db.add(obj)
    obj.api_key_encrypted = encrypt_token(api_key)
    obj.configurada = True
    db.flush()
    return True
