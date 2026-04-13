"""
Repositorio de acceso a datos para contactos_mkt.

CRUD puro via SQLAlchemy — sin lógica de negocio.
Todas las operaciones están aisladas por marca_id.
"""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from models.contacto_models import ContactoMkt

logger = logging.getLogger(__name__)


def _serialize(c: ContactoMkt) -> dict:
    return {
        "id": str(c.id),
        "marca_id": str(c.marca_id),
        "cliente_id": str(c.cliente_id),
        "nombre": c.nombre,
        "empresa": c.empresa,
        "cargo": c.cargo,
        "email_empresarial": c.email_empresarial,
        "email_personal": c.email_personal,
        "telefono_empresa": c.telefono_empresa,
        "telefono_personal": c.telefono_personal,
        "linkedin_url": c.linkedin_url,
        "confianza": c.confianza,
        "origen": c.origen,
        "score": c.score,
        "estado": c.estado,
        "notas": c.notas,
        "created_at": c.created_at.isoformat() if c.created_at else None,
    }


def listar_emails_por_marca(db: Session, marca_id: UUID) -> set[str]:
    """Retorna el set de emails empresariales ya guardados para una marca."""
    rows = db.execute(
        select(ContactoMkt.email_empresarial).where(
            ContactoMkt.marca_id == marca_id,
            ContactoMkt.email_empresarial.isnot(None),
        )
    ).scalars().all()
    return {e.lower().strip() for e in rows}


def listar(db: Session, marca_id: UUID) -> list[dict]:
    """Lista todos los contactos de una marca ordenados por fecha descendente."""
    logger.debug(f"[contactos_repo] listar marca_id={marca_id}")
    rows = (
        db.query(ContactoMkt)
        .filter(ContactoMkt.marca_id == marca_id)
        .order_by(ContactoMkt.created_at.desc())
        .all()
    )
    return [_serialize(r) for r in rows]


def crear(db: Session, data: dict) -> dict:
    """Crea un único contacto y retorna el dict serializado."""
    logger.debug(f"[contactos_repo] crear — empresa={data.get('empresa')!r}")
    contacto = ContactoMkt(**data)
    db.add(contacto)
    db.flush()
    return _serialize(contacto)


def crear_bulk(db: Session, contactos: list[dict]) -> list[dict]:
    """Inserta múltiples contactos en un solo flush. Retorna los dicts serializados."""
    logger.debug(f"[contactos_repo] crear_bulk — {len(contactos)} contactos")
    objs = [ContactoMkt(**c) for c in contactos]
    db.add_all(objs)
    db.flush()
    return [_serialize(o) for o in objs]


def buscar_por_email(db: Session, email: str, marca_id: UUID) -> Optional[dict]:
    """Busca un contacto por email empresarial dentro de una marca (case-insensitive)."""
    email_norm = email.lower().strip()
    row = (
        db.query(ContactoMkt)
        .filter(
            func.lower(ContactoMkt.email_empresarial) == email_norm,
            ContactoMkt.marca_id == marca_id,
        )
        .first()
    )
    return _serialize(row) if row else None


def buscar_por_id(db: Session, contacto_id: UUID, marca_id: UUID) -> Optional[ContactoMkt]:
    """Busca un contacto por ID verificando que pertenezca a la marca."""
    return (
        db.query(ContactoMkt)
        .filter(ContactoMkt.id == contacto_id, ContactoMkt.marca_id == marca_id)
        .first()
    )


def eliminar(db: Session, contacto_id: UUID, marca_id: UUID) -> bool:
    """Elimina un contacto por ID. Retorna True si existía, False si no."""
    logger.debug(f"[contactos_repo] eliminar id={contacto_id}")
    obj = buscar_por_id(db, contacto_id, marca_id)
    if not obj:
        return False
    db.delete(obj)
    db.flush()
    return True


def contar(db: Session, marca_id: UUID) -> int:
    """Retorna la cantidad de contactos de una marca."""
    return db.query(func.count(ContactoMkt.id)).filter(ContactoMkt.marca_id == marca_id).scalar() or 0
