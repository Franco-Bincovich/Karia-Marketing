"""Repositorio para config_reportes_mkt."""

from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy.orm import Session

from models.analytics_models import ConfigReportesMkt

logger = logging.getLogger(__name__)


def _s(c: ConfigReportesMkt) -> dict:
    """Serializa un ConfigReportesMkt a dict."""
    return {
        "id": str(c.id),
        "marca_id": str(c.marca_id),
        "frecuencia": c.frecuencia,
        "formatos": c.formatos,
        "canal_notificacion": c.canal_notificacion,
        "email_reporte": c.email_reporte,
        "whatsapp_reporte": c.whatsapp_reporte,
        "incluir_comparacion": c.incluir_comparacion,
        "periodo_comparacion": c.periodo_comparacion,
        "updated_at": c.updated_at.isoformat() if c.updated_at else None,
    }


def obtener_o_crear(db: Session, marca_id: UUID) -> dict:
    """Devuelve la config de reportes, creando defaults si no existe."""
    obj = db.query(ConfigReportesMkt).filter(ConfigReportesMkt.marca_id == marca_id).first()
    if not obj:
        obj = ConfigReportesMkt(marca_id=marca_id)
        db.add(obj)
        db.flush()
        logger.debug(f"[config_reportes_repo] creados defaults — marca={marca_id}")
    return _s(obj)


def actualizar(db: Session, marca_id: UUID, data: dict) -> dict:
    """Actualiza la configuración de reportes de una marca."""
    obj = db.query(ConfigReportesMkt).filter(ConfigReportesMkt.marca_id == marca_id).first()
    if not obj:
        obj = ConfigReportesMkt(marca_id=marca_id)
        db.add(obj)
    for k, v in data.items():
        if hasattr(obj, k) and k not in ("id", "marca_id"):
            setattr(obj, k, v)
    db.flush()
    return _s(obj)
