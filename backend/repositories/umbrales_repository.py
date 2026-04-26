"""Repositorio para umbrales_ads_mkt."""

from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy.orm import Session

from models.ads_models import UmbralesAdsMkt

logger = logging.getLogger(__name__)


def _s(u: UmbralesAdsMkt) -> dict:
    return {
        "id": str(u.id),
        "marca_id": str(u.marca_id),
        "cpa_maximo": float(u.cpa_maximo),
        "roas_minimo": float(u.roas_minimo),
        "gasto_diario_maximo": float(u.gasto_diario_maximo),
        "updated_at": u.updated_at.isoformat() if u.updated_at else None,
    }


def obtener_o_crear(db: Session, marca_id: UUID) -> dict:
    """Devuelve los umbrales de la marca, o nulls si no están configurados."""
    obj = db.query(UmbralesAdsMkt).filter(UmbralesAdsMkt.marca_id == marca_id).first()
    if not obj:
        return {
            "id": None,
            "marca_id": str(marca_id),
            "cpa_maximo": None,
            "roas_minimo": None,
            "gasto_diario_maximo": None,
            "updated_at": None,
        }
    return _s(obj)


def actualizar(db: Session, marca_id: UUID, data: dict) -> dict:
    """Actualiza los umbrales de una marca."""
    obj = db.query(UmbralesAdsMkt).filter(UmbralesAdsMkt.marca_id == marca_id).first()
    if not obj:
        obj = UmbralesAdsMkt(marca_id=marca_id)
        db.add(obj)
    for k, v in data.items():
        if hasattr(obj, k) and k not in ("id", "marca_id"):
            setattr(obj, k, v)
    db.flush()
    return _s(obj)
