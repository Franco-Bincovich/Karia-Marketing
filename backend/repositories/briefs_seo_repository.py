"""Repositorio CRUD para briefs_seo_mkt."""
from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy.orm import Session

from models.seo_models import BriefSeoMkt

logger = logging.getLogger(__name__)


def _s(b: BriefSeoMkt) -> dict:
    """Serializa un BriefSeoMkt a dict."""
    return {
        "id": str(b.id), "marca_id": str(b.marca_id),
        "keyword_principal": b.keyword_principal,
        "keywords_secundarias": b.keywords_secundarias,
        "intencion_busqueda": b.intencion_busqueda,
        "estructura_sugerida": b.estructura_sugerida,
        "longitud_minima": b.longitud_minima,
        "competidores_url": b.competidores_url,
        "meta_title": b.meta_title, "meta_description": b.meta_description,
        "usado": b.usado,
        "created_at": b.created_at.isoformat() if b.created_at else None,
    }


def crear(db: Session, data: dict) -> dict:
    """Crea un nuevo brief SEO."""
    obj = BriefSeoMkt(**data)
    db.add(obj)
    db.flush()
    logger.debug(f"[briefs_seo_repo] crear — keyword={data['keyword_principal']}")
    return _s(obj)


def listar(db: Session, marca_id: UUID) -> list:
    """Lista todos los briefs de una marca."""
    rows = db.query(BriefSeoMkt).filter(
        BriefSeoMkt.marca_id == marca_id
    ).order_by(BriefSeoMkt.created_at.desc()).all()
    return [_s(r) for r in rows]


def marcar_usado(db: Session, brief_id: UUID) -> dict:
    """Marca un brief como usado por el Agente Contenido."""
    obj = db.query(BriefSeoMkt).filter(BriefSeoMkt.id == brief_id).first()
    if not obj:
        return {}
    obj.usado = True
    db.flush()
    return _s(obj)
