"""Repositorio para config_listening_mkt."""
from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy.orm import Session

from models.comunidad_models import ConfigListeningMkt

logger = logging.getLogger(__name__)


def _s(c: ConfigListeningMkt) -> dict:
    """Serializa un ConfigListeningMkt a dict."""
    return {
        "id": str(c.id), "marca_id": str(c.marca_id),
        "terminos_marca": c.terminos_marca or [],
        "terminos_competidores": c.terminos_competidores or [],
        "keywords_sector": c.keywords_sector or [],
        "notificar_negativas": c.notificar_negativas,
        "notificar_competidores": c.notificar_competidores,
        "umbral_urgencia": c.umbral_urgencia,
        "updated_at": c.updated_at.isoformat() if c.updated_at else None,
    }


def obtener_o_crear(db: Session, marca_id: UUID) -> dict:
    """Devuelve la config de listening, creando defaults si no existe."""
    obj = db.query(ConfigListeningMkt).filter(ConfigListeningMkt.marca_id == marca_id).first()
    if not obj:
        obj = ConfigListeningMkt(marca_id=marca_id)
        db.add(obj)
        db.flush()
        logger.debug(f"[config_listening_repo] defaults creados — marca={marca_id}")
    return _s(obj)


def actualizar(db: Session, marca_id: UUID, data: dict) -> dict:
    """Actualiza la configuración de listening."""
    obj = db.query(ConfigListeningMkt).filter(ConfigListeningMkt.marca_id == marca_id).first()
    if not obj:
        obj = ConfigListeningMkt(marca_id=marca_id)
        db.add(obj)
    for k, v in data.items():
        if hasattr(obj, k) and k not in ("id", "marca_id"):
            setattr(obj, k, v)
    db.flush()
    return _s(obj)
