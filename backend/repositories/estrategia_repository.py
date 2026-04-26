"""Repositorio CRUD para estrategia_mkt."""

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from models.estrategia_models import EstrategiaMkt


def _s(e: EstrategiaMkt) -> dict:
    return {
        "id": str(e.id),
        "marca_id": str(e.marca_id),
        "tipo": e.tipo,
        "contenido": e.contenido,
        "periodo": e.periodo,
        "implementada": e.implementada,
        "activo": e.activo,
        "created_at": e.created_at.isoformat() if e.created_at else None,
    }


def crear(db: Session, data: dict) -> dict:
    obj = EstrategiaMkt(**data)
    db.add(obj)
    db.flush()
    return _s(obj)


def listar(db: Session, marca_id: UUID, tipo: Optional[str] = None) -> list[dict]:
    q = db.query(EstrategiaMkt).filter(EstrategiaMkt.marca_id == marca_id)
    if tipo:
        q = q.filter(EstrategiaMkt.tipo == tipo)
    return [_s(r) for r in q.order_by(EstrategiaMkt.created_at.desc()).all()]


def activar_plan(db: Session, estrategia_id: UUID, marca_id: UUID) -> Optional[dict]:
    """Activa un plan y desactiva todos los anteriores de la marca."""
    db.query(EstrategiaMkt).filter(
        EstrategiaMkt.marca_id == marca_id,
        EstrategiaMkt.tipo == "plan",
        EstrategiaMkt.activo == True,
    ).update({"activo": False})
    obj = (
        db.query(EstrategiaMkt)
        .filter(
            EstrategiaMkt.id == estrategia_id,
            EstrategiaMkt.marca_id == marca_id,
        )
        .first()
    )
    if not obj:
        return None
    obj.activo = True
    db.flush()
    return _s(obj)


def obtener_plan_activo(db: Session, marca_id: UUID) -> Optional[dict]:
    """Retorna el plan de contenido activo de la marca."""
    obj = (
        db.query(EstrategiaMkt)
        .filter(
            EstrategiaMkt.marca_id == marca_id,
            EstrategiaMkt.tipo == "plan",
            EstrategiaMkt.activo == True,
        )
        .first()
    )
    return _s(obj) if obj else None


def marcar_implementada(db: Session, estrategia_id: UUID, marca_id: UUID) -> Optional[dict]:
    obj = (
        db.query(EstrategiaMkt)
        .filter(
            EstrategiaMkt.id == estrategia_id,
            EstrategiaMkt.marca_id == marca_id,
        )
        .first()
    )
    if not obj:
        return None
    obj.implementada = True
    db.flush()
    return _s(obj)
