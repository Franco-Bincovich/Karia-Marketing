"""Repositorio CRUD para menciones_mkt."""
from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy.orm import Session

from models.comunidad_models import MencionMkt

logger = logging.getLogger(__name__)


def _s(m: MencionMkt) -> dict:
    """Serializa un MencionMkt a dict."""
    return {
        "id": str(m.id), "marca_id": str(m.marca_id),
        "tipo": m.tipo, "fuente": m.fuente, "url": m.url,
        "autor": m.autor, "contenido": m.contenido,
        "sentimiento": m.sentimiento, "alcance_estimado": m.alcance_estimado,
        "urgente": m.urgente, "procesado": m.procesado,
        "created_at": m.created_at.isoformat() if m.created_at else None,
    }


def crear_bulk(db: Session, menciones: list) -> list:
    """Crea múltiples menciones. Nada se descarta."""
    results = []
    for data in menciones:
        obj = MencionMkt(**data)
        db.add(obj)
        db.flush()
        results.append(_s(obj))
    logger.debug(f"[menciones_repo] crear_bulk — {len(menciones)} menciones")
    return results


def listar(db: Session, marca_id: UUID) -> list:
    """Lista todas las menciones de una marca."""
    rows = db.query(MencionMkt).filter(
        MencionMkt.marca_id == marca_id
    ).order_by(MencionMkt.created_at.desc()).all()
    return [_s(r) for r in rows]


def listar_urgentes(db: Session, marca_id: UUID) -> list:
    """Lista menciones urgentes no procesadas."""
    rows = db.query(MencionMkt).filter(
        MencionMkt.marca_id == marca_id,
        MencionMkt.urgente == True,
        MencionMkt.procesado == False,
    ).order_by(MencionMkt.created_at.desc()).all()
    return [_s(r) for r in rows]


def marcar_procesado(db: Session, mencion_id: UUID) -> dict:
    """Marca una mención como procesada."""
    obj = db.query(MencionMkt).filter(MencionMkt.id == mencion_id).first()
    if not obj:
        return {}
    obj.procesado = True
    db.flush()
    return _s(obj)
