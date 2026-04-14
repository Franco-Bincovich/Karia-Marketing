"""Repositorio para config_seo_mkt."""
from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy.orm import Session

from models.seo_models import ConfigSeoMkt

logger = logging.getLogger(__name__)


def _s(c: ConfigSeoMkt) -> dict:
    """Serializa un ConfigSeoMkt a dict."""
    return {
        "id": str(c.id), "marca_id": str(c.marca_id),
        "sitio_web": c.sitio_web, "frecuencia_reporte": c.frecuencia_reporte,
        "semrush_proyecto_id": c.semrush_proyecto_id,
        "search_console_conectado": c.search_console_conectado,
        "competidores": c.competidores,
        "updated_at": c.updated_at.isoformat() if c.updated_at else None,
    }


def obtener_o_crear(db: Session, marca_id: UUID) -> dict:
    """Devuelve la config SEO de la marca, creando defaults si no existe."""
    obj = db.query(ConfigSeoMkt).filter(ConfigSeoMkt.marca_id == marca_id).first()
    if not obj:
        obj = ConfigSeoMkt(marca_id=marca_id)
        db.add(obj)
        db.flush()
        logger.debug(f"[config_seo_repo] creados defaults — marca={marca_id}")
    return _s(obj)


def actualizar(db: Session, marca_id: UUID, data: dict) -> dict:
    """Actualiza la configuración SEO de una marca."""
    obj = db.query(ConfigSeoMkt).filter(ConfigSeoMkt.marca_id == marca_id).first()
    if not obj:
        obj = ConfigSeoMkt(marca_id=marca_id)
        db.add(obj)
    for k, v in data.items():
        if hasattr(obj, k) and k not in ("id", "marca_id"):
            setattr(obj, k, v)
    db.flush()
    return _s(obj)
