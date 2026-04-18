"""Repositorio CRUD para imagenes_mkt."""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from models.imagen_models import ImagenMkt

logger = logging.getLogger(__name__)


def _s(i: ImagenMkt) -> dict:
    return {
        "id": str(i.id),
        "marca_id": str(i.marca_id),
        "contenido_id": str(i.contenido_id) if i.contenido_id else None,
        "prompt": i.prompt,
        "imagen_url": i.imagen_url,
        "tamano": i.tamano,
        "estilo": i.estilo,
        "origen": i.origen or "ia",
        "created_at": i.created_at.isoformat() if i.created_at else None,
    }


def crear(db: Session, data: dict) -> dict:
    obj = ImagenMkt(**data)
    db.add(obj)
    db.flush()
    return _s(obj)


def listar(db: Session, marca_id: UUID) -> list[dict]:
    rows = db.query(ImagenMkt).filter(
        ImagenMkt.marca_id == marca_id,
    ).order_by(ImagenMkt.created_at.desc()).all()
    return [_s(r) for r in rows]


def listar_por_origen(db: Session, marca_id: UUID, origen: str) -> list[dict]:
    rows = db.query(ImagenMkt).filter(
        ImagenMkt.marca_id == marca_id, ImagenMkt.origen == origen,
    ).order_by(ImagenMkt.created_at.desc()).all()
    return [_s(r) for r in rows]


def eliminar(db: Session, imagen_id: UUID, marca_id: UUID) -> Optional[ImagenMkt]:
    obj = db.query(ImagenMkt).filter(ImagenMkt.id == imagen_id, ImagenMkt.marca_id == marca_id).first()
    if not obj:
        return None
    db.delete(obj)
    db.flush()
    return obj


def obtener(db: Session, imagen_id: UUID, marca_id: UUID) -> Optional[ImagenMkt]:
    return db.query(ImagenMkt).filter(
        ImagenMkt.id == imagen_id,
        ImagenMkt.marca_id == marca_id,
    ).first()
