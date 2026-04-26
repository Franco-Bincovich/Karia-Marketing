"""Repositorio CRUD para templates_mkt."""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from models.contenido_models import TemplatesMkt

logger = logging.getLogger(__name__)


def _s(t: TemplatesMkt) -> dict:
    return {
        "id": str(t.id),
        "marca_id": str(t.marca_id),
        "nombre": t.nombre,
        "red_social": t.red_social,
        "formato": t.formato,
        "copy": t.copy,
        "hashtags": t.hashtags,
        "tono": t.tono,
        "objetivo": t.objetivo,
        "usos": t.usos,
        "created_at": t.created_at.isoformat() if t.created_at else None,
    }


def crear(db: Session, data: dict) -> dict:
    """Crea un template para una marca."""
    obj = TemplatesMkt(**data)
    db.add(obj)
    db.flush()
    logger.debug(f"[templates_repo] crear — nombre={obj.nombre!r}")
    return _s(obj)


def listar(db: Session, marca_id: UUID) -> list[dict]:
    """Lista todos los templates de una marca ordenados por usos descendente."""
    rows = db.query(TemplatesMkt).filter(TemplatesMkt.marca_id == marca_id).order_by(TemplatesMkt.usos.desc()).all()
    return [_s(r) for r in rows]


def obtener(db: Session, template_id: UUID, marca_id: UUID) -> Optional[TemplatesMkt]:
    """Retorna el objeto ORM de un template verificando que pertenezca a la marca."""
    return db.query(TemplatesMkt).filter(TemplatesMkt.id == template_id, TemplatesMkt.marca_id == marca_id).first()


def eliminar(db: Session, template_id: UUID, marca_id: UUID) -> bool:
    """Elimina un template. Retorna True si existía."""
    obj = obtener(db, template_id, marca_id)
    if not obj:
        return False
    db.delete(obj)
    db.flush()
    return True


def incrementar_usos(db: Session, template_id: UUID) -> None:
    """Incrementa el contador de usos de un template."""
    obj = db.query(TemplatesMkt).filter(TemplatesMkt.id == template_id).first()
    if obj:
        obj.usos += 1
        db.flush()
