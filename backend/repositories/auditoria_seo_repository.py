"""Repositorio CRUD para auditoria_seo_mkt."""
from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy.orm import Session

from models.seo_models import AuditoriaSeoMkt

logger = logging.getLogger(__name__)


def _s(a: AuditoriaSeoMkt) -> dict:
    """Serializa un AuditoriaSeoMkt a dict."""
    return {
        "id": str(a.id), "marca_id": str(a.marca_id), "url": a.url,
        "tipo": a.tipo, "severidad": a.severidad,
        "descripcion": a.descripcion, "recomendacion": a.recomendacion,
        "implementado": a.implementado,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    }


def crear_bulk(db: Session, items: list) -> list:
    """Crea múltiples registros de auditoría SEO."""
    results = []
    for item in items:
        obj = AuditoriaSeoMkt(**item)
        db.add(obj)
        db.flush()
        results.append(_s(obj))
    logger.debug(f"[auditoria_seo_repo] crear_bulk — {len(items)} items")
    return results


def listar(db: Session, marca_id: UUID) -> list:
    """Lista todos los hallazgos de auditoría SEO de una marca."""
    rows = db.query(AuditoriaSeoMkt).filter(
        AuditoriaSeoMkt.marca_id == marca_id
    ).order_by(AuditoriaSeoMkt.created_at.desc()).all()
    return [_s(r) for r in rows]


def marcar_implementado(db: Session, item_id: UUID, marca_id: UUID) -> dict:
    """Marca un hallazgo como implementado por el cliente."""
    obj = db.query(AuditoriaSeoMkt).filter(
        AuditoriaSeoMkt.id == item_id, AuditoriaSeoMkt.marca_id == marca_id,
    ).first()
    if not obj:
        return {}
    obj.implementado = True
    db.flush()
    return _s(obj)


def listar_pendientes(db: Session, marca_id: UUID) -> list:
    """Lista hallazgos no implementados, ordenados por severidad."""
    orden = {"critico": 0, "alto": 1, "medio": 2, "bajo": 3}
    rows = db.query(AuditoriaSeoMkt).filter(
        AuditoriaSeoMkt.marca_id == marca_id, AuditoriaSeoMkt.implementado == False,
    ).all()
    return sorted([_s(r) for r in rows], key=lambda x: orden.get(x["severidad"], 4))
