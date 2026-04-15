"""Repositorio CRUD para publicaciones_mkt."""

import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.social_models import PublicacionesMkt

logger = logging.getLogger(__name__)


def _s(p: PublicacionesMkt) -> dict:
    return {
        "id": str(p.id), "marca_id": str(p.marca_id),
        "calendario_id": str(p.calendario_id) if p.calendario_id else None,
        "contenido_id": str(p.contenido_id) if p.contenido_id else None,
        "red_social": p.red_social,
        "post_id_externo": p.post_id_externo,
        "url_publicacion": p.url_publicacion,
        "copy_publicado": p.copy_publicado,
        "imagen_url": p.imagen_url,
        "estado": p.estado, "intentos": p.intentos,
        "error_detalle": p.error_detalle,
        "likes_2hs": p.likes_2hs, "comentarios_2hs": p.comentarios_2hs,
        "alcance_2hs": p.alcance_2hs, "engagement_bajo": p.engagement_bajo,
        "programado_para": p.programado_para.isoformat() if p.programado_para else None,
        "zernio_post_id": p.zernio_post_id,
        "publicado_at": p.publicado_at.isoformat() if p.publicado_at else None,
    }


def crear(db: Session, data: dict) -> dict:
    """Registra una nueva publicación realizada."""
    obj = PublicacionesMkt(**data)
    db.add(obj)
    db.flush()
    logger.debug(f"[publicaciones_repo] crear — id={obj.id}, red={obj.red_social}")
    return _s(obj)


def listar(db: Session, marca_id: UUID) -> list[dict]:
    """Lista todas las publicaciones de una marca, más recientes primero."""
    rows = (
        db.query(PublicacionesMkt)
        .filter(PublicacionesMkt.marca_id == marca_id)
        .order_by(PublicacionesMkt.publicado_at.desc())
        .all()
    )
    return [_s(r) for r in rows]


def actualizar_metricas(db: Session, pub_id: UUID, metricas: dict) -> dict:
    """
    Actualiza las métricas de las primeras 2hs de una publicación.

    Args:
        metricas: Dict con likes, comentarios, alcance, engagement_bajo
    """
    obj = db.query(PublicacionesMkt).filter(PublicacionesMkt.id == pub_id).first()
    if not obj:
        return {}
    obj.likes_2hs = metricas.get("likes", 0)
    obj.comentarios_2hs = metricas.get("comentarios", 0)
    obj.alcance_2hs = metricas.get("alcance", 0)
    obj.engagement_bajo = metricas.get("engagement_bajo", False)
    db.flush()
    return _s(obj)


def actualizar_estado(db: Session, pub_id: UUID, estado: str, error: str = None, intentos: int = None) -> dict:
    """Actualiza estado, detalle de error e intentos de una publicación."""
    obj = db.query(PublicacionesMkt).filter(PublicacionesMkt.id == pub_id).first()
    if not obj:
        return {}
    obj.estado = estado
    if error is not None:
        obj.error_detalle = error
    if intentos is not None:
        obj.intentos = intentos
    db.flush()
    return _s(obj)


def contar_mes_actual(db: Session, marca_id: UUID) -> int:
    """Cuenta publicaciones (publicadas + programadas) del mes actual para la marca."""
    ahora = datetime.now(timezone.utc)
    inicio_mes = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return db.query(func.count(PublicacionesMkt.id)).filter(
        PublicacionesMkt.marca_id == marca_id,
        PublicacionesMkt.created_at >= inicio_mes,
        PublicacionesMkt.estado.in_(["publicado", "programado"]),
    ).scalar() or 0


def promedio_engagement(db: Session, marca_id: UUID) -> float:
    """Calcula el promedio histórico de engagement (likes+comentarios) por publicación."""
    result = db.query(
        func.avg(PublicacionesMkt.likes_2hs + PublicacionesMkt.comentarios_2hs)
    ).filter(
        PublicacionesMkt.marca_id == marca_id,
        PublicacionesMkt.estado == "publicado",
    ).scalar()
    return float(result or 0)
