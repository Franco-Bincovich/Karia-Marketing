"""Repositorio CRUD para menciones_mkt."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from models.comunidad_models import MencionMkt

logger = logging.getLogger(__name__)


def _s(m: MencionMkt) -> dict:
    """Serializa un MencionMkt a dict."""
    return {
        "id": str(m.id),
        "marca_id": str(m.marca_id),
        "tipo": m.tipo,
        "fuente": m.fuente,
        "url": m.url,
        "autor": m.autor,
        "contenido": m.contenido,
        "sentimiento": m.sentimiento,
        "score_sentimiento": m.score_sentimiento,
        "alcance_estimado": m.alcance_estimado,
        "urgente": m.urgente,
        "procesado": m.procesado,
        "alerta_generada": m.alerta_generada,
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
    rows = db.query(MencionMkt).filter(MencionMkt.marca_id == marca_id).order_by(MencionMkt.created_at.desc()).all()
    return [_s(r) for r in rows]


def listar_urgentes(db: Session, marca_id: UUID) -> list:
    """Lista menciones urgentes no procesadas."""
    rows = (
        db.query(MencionMkt)
        .filter(
            MencionMkt.marca_id == marca_id,
            MencionMkt.urgente == True,
            MencionMkt.procesado == False,
        )
        .order_by(MencionMkt.created_at.desc())
        .all()
    )
    return [_s(r) for r in rows]


def listar_filtrado(
    db: Session,
    marca_id: UUID,
    sentimiento: Optional[str] = None,
    plataforma: Optional[str] = None,
    desde: Optional[datetime] = None,
) -> list:
    """Lista menciones con filtros opcionales."""
    q = db.query(MencionMkt).filter(MencionMkt.marca_id == marca_id)
    if sentimiento:
        q = q.filter(MencionMkt.sentimiento == sentimiento)
    if plataforma:
        q = q.filter(MencionMkt.fuente == plataforma)
    if desde:
        q = q.filter(MencionMkt.created_at >= desde)
    return [_s(r) for r in q.order_by(MencionMkt.created_at.desc()).limit(100).all()]


def contar_por_sentimiento(db: Session, marca_id: UUID) -> dict:
    """Cuenta menciones por tipo de sentimiento."""
    from sqlalchemy import func

    rows = (
        db.query(MencionMkt.sentimiento, func.count().label("n"))
        .filter(
            MencionMkt.marca_id == marca_id,
        )
        .group_by(MencionMkt.sentimiento)
        .all()
    )
    return {s: n for s, n in rows}


def total_menciones(db: Session, marca_id: UUID) -> int:
    from sqlalchemy import func

    return db.query(func.count(MencionMkt.id)).filter(MencionMkt.marca_id == marca_id).scalar() or 0


def marcar_procesado(db: Session, mencion_id: UUID) -> dict:
    """Marca una mención como procesada."""
    obj = db.query(MencionMkt).filter(MencionMkt.id == mencion_id).first()
    if not obj:
        return {}
    obj.procesado = True
    db.flush()
    return _s(obj)
