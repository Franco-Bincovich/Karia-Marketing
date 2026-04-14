"""Repositorio CRUD para alertas_mkt."""
from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy.orm import Session

from models.analytics_models import AlertaMkt

logger = logging.getLogger(__name__)


def _s(a: AlertaMkt) -> dict:
    """Serializa un AlertaMkt a dict."""
    return {
        "id": str(a.id), "marca_id": str(a.marca_id),
        "tipo": a.tipo, "canal": a.canal, "mensaje": a.mensaje,
        "datos": a.datos, "leida": a.leida,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    }


def crear(db: Session, data: dict) -> dict:
    """Crea una nueva alerta."""
    obj = AlertaMkt(**data)
    db.add(obj)
    db.flush()
    logger.debug(f"[alertas_repo] crear — tipo={data['tipo']}")
    return _s(obj)


def listar(db: Session, marca_id: UUID) -> list:
    """Lista todas las alertas de una marca."""
    rows = db.query(AlertaMkt).filter(
        AlertaMkt.marca_id == marca_id
    ).order_by(AlertaMkt.created_at.desc()).all()
    return [_s(r) for r in rows]


def marcar_leida(db: Session, alerta_id: UUID, marca_id: UUID) -> dict:
    """Marca una alerta como leída."""
    obj = db.query(AlertaMkt).filter(
        AlertaMkt.id == alerta_id, AlertaMkt.marca_id == marca_id,
    ).first()
    if not obj:
        return {}
    obj.leida = True
    db.flush()
    return _s(obj)


def listar_no_leidas(db: Session, marca_id: UUID) -> list:
    """Lista alertas no leídas de una marca."""
    rows = db.query(AlertaMkt).filter(
        AlertaMkt.marca_id == marca_id, AlertaMkt.leida == False,
    ).order_by(AlertaMkt.created_at.desc()).all()
    return [_s(r) for r in rows]
