"""Repositorio CRUD para calendario_editorial_mkt."""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from models.social_models import CalendarioEditorialMkt

logger = logging.getLogger(__name__)


def _s(c: CalendarioEditorialMkt) -> dict:
    return {
        "id": str(c.id),
        "marca_id": str(c.marca_id),
        "cliente_id": str(c.cliente_id),
        "contenido_id": str(c.contenido_id) if c.contenido_id else None,
        "titulo": c.titulo,
        "descripcion": c.descripcion,
        "red_social": c.red_social,
        "formato": c.formato,
        "fecha_programada": c.fecha_programada.isoformat() if c.fecha_programada else None,
        "estado": c.estado,
        "created_at": c.created_at.isoformat() if c.created_at else None,
    }


def crear_evento(db: Session, evento: dict) -> dict:
    """Crea un evento en el calendario editorial."""
    obj = CalendarioEditorialMkt(**evento)
    db.add(obj)
    db.flush()
    logger.debug(f"[calendario_repo] crear_evento — id={obj.id}")
    return _s(obj)


def listar(db: Session, marca_id: UUID, mes: int, anio: int) -> list[dict]:
    """Lista eventos de una marca filtrados por mes y año."""
    from sqlalchemy import extract

    rows = (
        db.query(CalendarioEditorialMkt)
        .filter(
            CalendarioEditorialMkt.marca_id == marca_id,
            extract("month", CalendarioEditorialMkt.fecha_programada) == mes,
            extract("year", CalendarioEditorialMkt.fecha_programada) == anio,
        )
        .order_by(CalendarioEditorialMkt.fecha_programada.asc())
        .all()
    )
    return [_s(r) for r in rows]


def obtener(db: Session, evento_id: UUID, marca_id: UUID) -> Optional[CalendarioEditorialMkt]:
    """Retorna el objeto ORM de un evento verificando que pertenezca a la marca."""
    return (
        db.query(CalendarioEditorialMkt)
        .filter(
            CalendarioEditorialMkt.id == evento_id,
            CalendarioEditorialMkt.marca_id == marca_id,
        )
        .first()
    )


def actualizar_estado(db: Session, evento_id: UUID, estado: str) -> Optional[dict]:
    """Actualiza el estado de un evento del calendario."""
    obj = db.query(CalendarioEditorialMkt).filter(CalendarioEditorialMkt.id == evento_id).first()
    if not obj:
        return None
    obj.estado = estado
    db.flush()
    return _s(obj)


def eliminar(db: Session, evento_id: UUID, marca_id: UUID) -> bool:
    """Elimina un evento. Retorna True si existía."""
    obj = obtener(db, evento_id, marca_id)
    if not obj:
        return False
    db.delete(obj)
    db.flush()
    return True


def listar_programados_pendientes(db: Session) -> list[dict]:
    """
    Lista todos los eventos con estado 'programado' cuya fecha ya pasó.
    Usado por el scheduler para publicar automáticamente.
    """
    from datetime import datetime, timezone

    ahora = datetime.now(timezone.utc)
    rows = (
        db.query(CalendarioEditorialMkt)
        .filter(
            CalendarioEditorialMkt.estado == "programado",
            CalendarioEditorialMkt.fecha_programada <= ahora,
        )
        .all()
    )
    return [_s(r) for r in rows]
