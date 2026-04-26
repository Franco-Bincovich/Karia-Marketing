"""Repositorio CRUD para reportes_mkt."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from models.analytics_models import ReporteMkt

logger = logging.getLogger(__name__)


def _s(r: ReporteMkt) -> dict:
    """Serializa un ReporteMkt a dict."""
    return {
        "id": str(r.id),
        "marca_id": str(r.marca_id),
        "tipo": r.tipo,
        "periodo_inicio": r.periodo_inicio.isoformat(),
        "periodo_fin": r.periodo_fin.isoformat(),
        "contenido": r.contenido,
        "resumen_ejecutivo": r.resumen_ejecutivo,
        "formato": r.formato,
        "enviado": r.enviado,
        "enviado_at": r.enviado_at.isoformat() if r.enviado_at else None,
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }


def crear(db: Session, data: dict) -> dict:
    """Crea un nuevo reporte."""
    obj = ReporteMkt(**data)
    db.add(obj)
    db.flush()
    logger.debug(f"[reportes_repo] crear — tipo={data['tipo']}")
    return _s(obj)


def listar(db: Session, marca_id: UUID) -> list:
    """Lista reportes de una marca, más recientes primero."""
    rows = db.query(ReporteMkt).filter(ReporteMkt.marca_id == marca_id).order_by(ReporteMkt.created_at.desc()).all()
    return [_s(r) for r in rows]


def marcar_enviado(db: Session, reporte_id: UUID) -> dict:
    """Marca un reporte como enviado."""
    obj = db.query(ReporteMkt).filter(ReporteMkt.id == reporte_id).first()
    if not obj:
        return {}
    obj.enviado = True
    obj.enviado_at = datetime.now(timezone.utc)
    db.flush()
    return _s(obj)
