"""Repositorio CRUD para aprendizaje_mkt — motor de autoaprendizaje."""

import logging
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.contenido_models import AprendizajeMkt

logger = logging.getLogger(__name__)


def _s(a: AprendizajeMkt) -> dict:
    return {
        "id": str(a.id),
        "marca_id": str(a.marca_id),
        "contenido_id": str(a.contenido_id) if a.contenido_id else None,
        "tipo": a.tipo,
        "red_social": a.red_social,
        "formato": a.formato,
        "tono": a.tono,
        "comentario": a.comentario,
        "copy_original": a.copy_original,
        "copy_final": a.copy_final,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    }


def registrar(db: Session, evento: dict) -> dict:
    """
    Registra un evento de aprendizaje (aprobacion, rechazo o edicion).

    Args:
        evento: Dict con marca_id, tipo y campos opcionales del contexto

    Returns:
        Evento serializado con id asignado
    """
    obj = AprendizajeMkt(**evento)
    db.add(obj)
    db.flush()
    logger.debug(f"[aprendizaje_repo] registrar — tipo={obj.tipo}, marca={obj.marca_id}")
    return _s(obj)


def listar_por_marca(db: Session, marca_id: UUID) -> list[dict]:
    """Lista todos los eventos de aprendizaje de una marca, más recientes primero."""
    rows = db.query(AprendizajeMkt).filter(AprendizajeMkt.marca_id == marca_id).order_by(AprendizajeMkt.created_at.desc()).all()
    return [_s(r) for r in rows]


def obtener_preferencias(db: Session, marca_id: UUID) -> dict:
    """
    Agrega los eventos de aprendizaje en un resumen de preferencias de la marca.

    Útil para enriquecer el prompt de generación con historial real.

    Returns:
        Dict con conteos por tipo, tono más aprobado y red social más activa
    """
    base = db.query(AprendizajeMkt).filter(AprendizajeMkt.marca_id == marca_id)

    totales = base.with_entities(AprendizajeMkt.tipo, func.count().label("n")).group_by(AprendizajeMkt.tipo).all()

    tono_top = (
        base.filter(AprendizajeMkt.tipo == "aprobacion", AprendizajeMkt.tono.isnot(None))
        .with_entities(AprendizajeMkt.tono, func.count().label("n"))
        .group_by(AprendizajeMkt.tono)
        .order_by(func.count().desc())
        .first()
    )

    red_top = (
        base.filter(AprendizajeMkt.red_social.isnot(None))
        .with_entities(AprendizajeMkt.red_social, func.count().label("n"))
        .group_by(AprendizajeMkt.red_social)
        .order_by(func.count().desc())
        .first()
    )

    conteos = {t: n for t, n in totales}
    return {
        "aprobaciones": conteos.get("aprobacion", 0),
        "rechazos": conteos.get("rechazo", 0),
        "ediciones": conteos.get("edicion", 0),
        "tono_preferido": tono_top[0] if tono_top else None,
        "red_social_mas_activa": red_top[0] if red_top else None,
    }
