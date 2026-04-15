"""Repositorio CRUD para mensajes_comunidad_mkt."""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from models.comunidad_models import MensajeComunidadMkt

logger = logging.getLogger(__name__)


def _s(m: MensajeComunidadMkt) -> dict:
    """Serializa un MensajeComunidadMkt a dict."""
    return {
        "id": str(m.id), "marca_id": str(m.marca_id),
        "red_social": m.red_social, "tipo": m.tipo,
        "autor_username": m.autor_username, "autor_id_externo": m.autor_id_externo,
        "contenido": m.contenido, "clasificacion": m.clasificacion,
        "sentimiento": m.sentimiento, "respuesta": m.respuesta,
        "respondido": m.respondido, "escalado": m.escalado,
        "motivo_escalado": m.motivo_escalado, "es_lead": m.es_lead,
        "created_at": m.created_at.isoformat() if m.created_at else None,
        "respondido_at": m.respondido_at.isoformat() if m.respondido_at else None,
    }


def crear(db: Session, data: dict) -> dict:
    """Crea un nuevo mensaje de comunidad."""
    obj = MensajeComunidadMkt(**data)
    db.add(obj)
    db.flush()
    logger.debug(f"[mensajes_repo] crear — tipo={data['tipo']}")
    return _s(obj)


def listar(db: Session, marca_id: UUID) -> list:
    """Lista todos los mensajes de una marca."""
    rows = db.query(MensajeComunidadMkt).filter(
        MensajeComunidadMkt.marca_id == marca_id
    ).order_by(MensajeComunidadMkt.created_at.desc()).all()
    return [_s(r) for r in rows]


def listar_pendientes(db: Session, marca_id: UUID) -> list:
    """Lista mensajes pendientes de respuesta."""
    rows = db.query(MensajeComunidadMkt).filter(
        MensajeComunidadMkt.marca_id == marca_id,
        MensajeComunidadMkt.respondido == False,
        MensajeComunidadMkt.escalado == False,
    ).order_by(MensajeComunidadMkt.created_at.asc()).all()
    return [_s(r) for r in rows]


def marcar_respondido(db: Session, msg_id: UUID, respuesta: str) -> dict:
    """Marca un mensaje como respondido con la respuesta dada."""
    obj = db.query(MensajeComunidadMkt).filter(MensajeComunidadMkt.id == msg_id).first()
    if not obj:
        return {}
    obj.respuesta = respuesta
    obj.respondido = True
    obj.respondido_at = datetime.now(timezone.utc)
    db.flush()
    return _s(obj)


def marcar_escalado(db: Session, msg_id: UUID, motivo: str) -> dict:
    """Marca un mensaje como escalado con motivo."""
    obj = db.query(MensajeComunidadMkt).filter(MensajeComunidadMkt.id == msg_id).first()
    if not obj:
        return {}
    obj.escalado = True
    obj.motivo_escalado = motivo
    db.flush()
    return _s(obj)


def listar_respondidos(db: Session, marca_id: UUID) -> list:
    """Lista mensajes respondidos o ignorados (historial gestionado)."""
    rows = db.query(MensajeComunidadMkt).filter(
        MensajeComunidadMkt.marca_id == marca_id,
        MensajeComunidadMkt.respondido == True,  # noqa: E712
    ).order_by(MensajeComunidadMkt.respondido_at.desc()).all()
    return [_s(r) for r in rows]


def listar_leads(db: Session, marca_id: UUID) -> list:
    """Lista mensajes detectados como leads."""
    rows = db.query(MensajeComunidadMkt).filter(
        MensajeComunidadMkt.marca_id == marca_id,
        MensajeComunidadMkt.es_lead == True,
    ).order_by(MensajeComunidadMkt.created_at.desc()).all()
    return [_s(r) for r in rows]
