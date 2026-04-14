"""Repositorio CRUD para campanas_ads_mkt."""
from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy.orm import Session

from models.ads_models import CampanaAdsMkt

logger = logging.getLogger(__name__)


def _s(c: CampanaAdsMkt) -> dict:
    return {
        "id": str(c.id), "marca_id": str(c.marca_id), "cliente_id": str(c.cliente_id),
        "nombre": c.nombre, "plataforma": c.plataforma, "objetivo": c.objetivo,
        "presupuesto_diario": float(c.presupuesto_diario),
        "presupuesto_mensual": float(c.presupuesto_mensual) if c.presupuesto_mensual else None,
        "campaign_id_externo": c.campaign_id_externo, "estado": c.estado,
        "aprobada_por": str(c.aprobada_por) if c.aprobada_por else None,
        "aprobada_at": c.aprobada_at.isoformat() if c.aprobada_at else None,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "updated_at": c.updated_at.isoformat() if c.updated_at else None,
    }


def crear(db: Session, data: dict) -> dict:
    obj = CampanaAdsMkt(**data)
    db.add(obj)
    db.flush()
    logger.debug(f"[campanas_repo] crear — id={obj.id}")
    return _s(obj)


def listar(db: Session, marca_id: UUID) -> list:
    rows = (
        db.query(CampanaAdsMkt)
        .filter(CampanaAdsMkt.marca_id == marca_id)
        .order_by(CampanaAdsMkt.created_at.desc())
        .all()
    )
    return [_s(r) for r in rows]


def obtener(db: Session, campana_id: UUID, marca_id: UUID):
    return (
        db.query(CampanaAdsMkt)
        .filter(CampanaAdsMkt.id == campana_id, CampanaAdsMkt.marca_id == marca_id)
        .first()
    )


def actualizar_estado(db: Session, campana_id: UUID, estado: str, **kwargs) -> dict:
    obj = db.query(CampanaAdsMkt).filter(CampanaAdsMkt.id == campana_id).first()
    if not obj:
        return {}
    obj.estado = estado
    for k, v in kwargs.items():
        if hasattr(obj, k):
            setattr(obj, k, v)
    db.flush()
    return _s(obj)


def listar_activas(db: Session, marca_id: UUID) -> list:
    rows = (
        db.query(CampanaAdsMkt)
        .filter(CampanaAdsMkt.marca_id == marca_id, CampanaAdsMkt.estado == "activa")
        .all()
    )
    return [_s(r) for r in rows]
