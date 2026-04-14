"""Repositorio para config_comunidad_mkt."""
from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy.orm import Session

from models.comunidad_models import ConfigComunidadMkt

logger = logging.getLogger(__name__)


def _s(c: ConfigComunidadMkt) -> dict:
    """Serializa un ConfigComunidadMkt a dict."""
    return {
        "id": str(c.id), "marca_id": str(c.marca_id),
        "criterios_escalado": c.criterios_escalado or [],
        "tiempo_respuesta_max": c.tiempo_respuesta_max,
        "responder_agresivos": c.responder_agresivos,
        "responder_spam": c.responder_spam, "modo": c.modo,
        "updated_at": c.updated_at.isoformat() if c.updated_at else None,
    }


def obtener_o_crear(db: Session, marca_id: UUID) -> dict:
    """Devuelve la config de comunidad, creando defaults si no existe."""
    obj = db.query(ConfigComunidadMkt).filter(ConfigComunidadMkt.marca_id == marca_id).first()
    if not obj:
        obj = ConfigComunidadMkt(marca_id=marca_id)
        db.add(obj)
        db.flush()
        logger.debug(f"[config_comunidad_repo] defaults creados — marca={marca_id}")
    return _s(obj)


def actualizar(db: Session, marca_id: UUID, data: dict) -> dict:
    """Actualiza la configuración de comunidad."""
    obj = db.query(ConfigComunidadMkt).filter(ConfigComunidadMkt.marca_id == marca_id).first()
    if not obj:
        obj = ConfigComunidadMkt(marca_id=marca_id)
        db.add(obj)
    for k, v in data.items():
        if hasattr(obj, k) and k not in ("id", "marca_id"):
            setattr(obj, k, v)
    db.flush()
    return _s(obj)
