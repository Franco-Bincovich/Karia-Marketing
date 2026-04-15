"""Repositorio CRUD para contenido_mkt y versiones_contenido_mkt."""

import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.contenido_models import ContenidoMkt, VersionesContenidoMkt

logger = logging.getLogger(__name__)


def _s(c: ContenidoMkt) -> dict:
    return {
        "id": str(c.id), "marca_id": str(c.marca_id), "cliente_id": str(c.cliente_id),
        "red_social": c.red_social, "formato": c.formato, "objetivo": c.objetivo,
        "tono": c.tono, "tema": c.tema,
        "copy_a": c.copy_a, "copy_b": c.copy_b, "copy_c": c.copy_c,
        "hashtags_a": c.hashtags_a, "hashtags_b": c.hashtags_b, "hashtags_c": c.hashtags_c,
        "cta_a": c.cta_a, "cta_b": c.cta_b, "cta_c": c.cta_c,
        "imagen_url": c.imagen_url,
        "variante_seleccionada": c.variante_seleccionada,
        "estado": c.estado, "modo": c.modo,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "updated_at": c.updated_at.isoformat() if c.updated_at else None,
    }


def _sv(v: VersionesContenidoMkt) -> dict:
    return {
        "id": str(v.id), "contenido_id": str(v.contenido_id),
        "version": v.version, "copy_a": v.copy_a, "copy_b": v.copy_b,
        "motivo_rechazo": v.motivo_rechazo, "creado_por": v.creado_por,
        "created_at": v.created_at.isoformat() if v.created_at else None,
    }


def crear(db: Session, data: dict) -> dict:
    """Crea una pieza de contenido y retorna el dict serializado."""
    obj = ContenidoMkt(**data)
    db.add(obj)
    db.flush()
    logger.debug(f"[contenido_repo] crear — id={obj.id}")
    return _s(obj)


def listar(db: Session, marca_id: UUID, estado: Optional[str] = None) -> list[dict]:
    """Lista contenido de una marca con filtro opcional de estado."""
    q = db.query(ContenidoMkt).filter(ContenidoMkt.marca_id == marca_id)
    if estado:
        q = q.filter(ContenidoMkt.estado == estado)
    rows = q.order_by(ContenidoMkt.created_at.desc()).all()
    return [_s(r) for r in rows]


def contar_mes_actual(db: Session, marca_id: UUID) -> int:
    """Cuenta contenido aprobado + publicado del mes actual."""
    ahora = datetime.now(timezone.utc)
    inicio_mes = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return db.query(func.count(ContenidoMkt.id)).filter(
        ContenidoMkt.marca_id == marca_id,
        ContenidoMkt.created_at >= inicio_mes,
        ContenidoMkt.estado.in_(["aprobado", "publicado"]),
    ).scalar() or 0


def obtener(db: Session, contenido_id: UUID, marca_id: UUID) -> Optional[ContenidoMkt]:
    """Retorna el objeto ORM de una pieza verificando que pertenezca a la marca."""
    return db.query(ContenidoMkt).filter(
        ContenidoMkt.id == contenido_id, ContenidoMkt.marca_id == marca_id
    ).first()


def actualizar_campos(db: Session, obj: ContenidoMkt, campos: dict) -> dict:
    """Actualiza campos arbitrarios sobre un objeto ya obtenido."""
    for k, v in campos.items():
        setattr(obj, k, v)
    db.flush()
    return _s(obj)


def eliminar(db: Session, contenido_id: UUID, marca_id: UUID) -> bool:
    """Elimina una pieza de contenido. Retorna True si existía."""
    obj = obtener(db, contenido_id, marca_id)
    if not obj:
        return False
    db.delete(obj)
    db.flush()
    return True


def guardar_version(db: Session, contenido_id: UUID, version_data: dict) -> dict:
    """Guarda una nueva versión de contenido. Autoincrementa el número de versión."""
    ultimo = (
        db.query(func.max(VersionesContenidoMkt.version))
        .filter(VersionesContenidoMkt.contenido_id == contenido_id)
        .scalar() or 0
    )
    v = VersionesContenidoMkt(contenido_id=contenido_id, version=ultimo + 1, **version_data)
    db.add(v)
    db.flush()
    logger.debug(f"[contenido_repo] guardar_version — contenido={contenido_id}, v={v.version}")
    return _sv(v)


def listar_versiones(db: Session, contenido_id: UUID) -> list[dict]:
    """Lista todas las versiones de una pieza ordenadas por número ascendente."""
    rows = (
        db.query(VersionesContenidoMkt)
        .filter(VersionesContenidoMkt.contenido_id == contenido_id)
        .order_by(VersionesContenidoMkt.version.asc())
        .all()
    )
    return [_sv(r) for r in rows]
