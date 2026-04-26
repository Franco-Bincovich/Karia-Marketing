"""Repositorio CRUD para ads_mkt."""

from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy.orm import Session

from models.ads_models import AdMkt

logger = logging.getLogger(__name__)


def _s(a: AdMkt) -> dict:
    return {
        "id": str(a.id),
        "campana_id": str(a.campana_id),
        "marca_id": str(a.marca_id),
        "nombre": a.nombre,
        "copy_titulo": a.copy_titulo,
        "copy_descripcion": a.copy_descripcion,
        "imagen_url": a.imagen_url,
        "ad_id_externo": a.ad_id_externo,
        "variante": a.variante,
        "estado": a.estado,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    }


def crear(db: Session, data: dict) -> dict:
    obj = AdMkt(**data)
    db.add(obj)
    db.flush()
    logger.debug(f"[ads_repo] crear — id={obj.id}")
    return _s(obj)


def listar_por_campana(db: Session, campana_id: UUID) -> list:
    rows = db.query(AdMkt).filter(AdMkt.campana_id == campana_id).order_by(AdMkt.created_at.desc()).all()
    return [_s(r) for r in rows]


def actualizar_estado(db: Session, ad_id: UUID, estado: str) -> dict:
    obj = db.query(AdMkt).filter(AdMkt.id == ad_id).first()
    if not obj:
        return {}
    obj.estado = estado
    db.flush()
    return _s(obj)
