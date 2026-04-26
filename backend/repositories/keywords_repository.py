"""Repositorio CRUD para keywords_mkt."""

from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy.orm import Session

from models.seo_models import KeywordMkt

logger = logging.getLogger(__name__)


def _s(k: KeywordMkt) -> dict:
    """Serializa un KeywordMkt a dict."""
    return {
        "id": str(k.id),
        "marca_id": str(k.marca_id),
        "keyword": k.keyword,
        "volumen_mensual": k.volumen_mensual,
        "dificultad": k.dificultad,
        "intencion": k.intencion,
        "posicion_actual": k.posicion_actual,
        "posicion_anterior": k.posicion_anterior,
        "clicks_organicos": k.clicks_organicos,
        "impresiones": k.impresiones,
        "ctr": float(k.ctr),
        "url_objetivo": k.url_objetivo,
        "estado": k.estado,
        "created_at": k.created_at.isoformat() if k.created_at else None,
        "updated_at": k.updated_at.isoformat() if k.updated_at else None,
    }


def crear_o_actualizar(db: Session, marca_id: UUID, data: dict) -> dict:
    """Crea keyword o actualiza si ya existe para la marca."""
    obj = (
        db.query(KeywordMkt)
        .filter(
            KeywordMkt.marca_id == marca_id,
            KeywordMkt.keyword == data["keyword"],
        )
        .first()
    )
    if obj:
        for k, v in data.items():
            if hasattr(obj, k) and k not in ("id", "marca_id", "keyword"):
                setattr(obj, k, v)
        db.flush()
        return _s(obj)
    obj = KeywordMkt(marca_id=marca_id, **data)
    db.add(obj)
    db.flush()
    logger.debug(f"[keywords_repo] crear — keyword={data['keyword']}")
    return _s(obj)


def listar(db: Session, marca_id: UUID) -> list:
    """Lista todas las keywords de una marca."""
    rows = db.query(KeywordMkt).filter(KeywordMkt.marca_id == marca_id).order_by(KeywordMkt.volumen_mensual.desc()).all()
    return [_s(r) for r in rows]


def listar_por_estado(db: Session, marca_id: UUID, estado: str) -> list:
    """Lista keywords filtradas por estado."""
    rows = db.query(KeywordMkt).filter(KeywordMkt.marca_id == marca_id, KeywordMkt.estado == estado).all()
    return [_s(r) for r in rows]


def actualizar_posicion(db: Session, keyword_id: UUID, posicion: int) -> dict:
    """Actualiza posición actual, guardando la anterior."""
    obj = db.query(KeywordMkt).filter(KeywordMkt.id == keyword_id).first()
    if not obj:
        return {}
    obj.posicion_anterior = obj.posicion_actual
    obj.posicion_actual = posicion
    db.flush()
    return _s(obj)


def eliminar(db: Session, keyword_id: UUID, marca_id: UUID) -> bool:
    """Elimina una keyword verificando pertenencia a la marca."""
    deleted = db.query(KeywordMkt).filter(KeywordMkt.id == keyword_id, KeywordMkt.marca_id == marca_id).delete()
    db.flush()
    return deleted > 0
