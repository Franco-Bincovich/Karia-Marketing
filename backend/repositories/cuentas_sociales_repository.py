"""Repositorio CRUD para cuentas_sociales_mkt."""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from models.social_models import CuentasSocialesMkt

logger = logging.getLogger(__name__)


def _s(c: CuentasSocialesMkt) -> dict:
    """Serializa sin exponer el access_token_encrypted."""
    return {
        "id": str(c.id), "marca_id": str(c.marca_id),
        "red_social": c.red_social, "nombre_cuenta": c.nombre_cuenta,
        "account_id_externo": c.account_id_externo,
        "token_expires_at": c.token_expires_at.isoformat() if c.token_expires_at else None,
        "activa": c.activa,
        "tiene_token": bool(c.access_token_encrypted),
        "created_at": c.created_at.isoformat() if c.created_at else None,
    }


def crear_o_actualizar(db: Session, cuenta: dict) -> dict:
    """
    Upsert de cuenta social por (marca_id, red_social).
    Si ya existe la actualiza; si no, la crea.
    El access_token_encrypted debe venir ya encriptado.
    """
    marca_id = cuenta["marca_id"]
    red_social = cuenta["red_social"]

    obj = db.query(CuentasSocialesMkt).filter(
        CuentasSocialesMkt.marca_id == marca_id,
        CuentasSocialesMkt.red_social == red_social,
    ).first()

    if obj:
        for k, v in cuenta.items():
            setattr(obj, k, v)
        logger.debug(f"[cuentas_repo] actualizar — marca={marca_id}, red={red_social}")
    else:
        obj = CuentasSocialesMkt(**cuenta)
        db.add(obj)
        logger.debug(f"[cuentas_repo] crear — marca={marca_id}, red={red_social}")

    db.flush()
    return _s(obj)


def listar(db: Session, marca_id: UUID) -> list[dict]:
    """Lista todas las cuentas sociales de una marca (sin exponer tokens)."""
    rows = db.query(CuentasSocialesMkt).filter(CuentasSocialesMkt.marca_id == marca_id).all()
    return [_s(r) for r in rows]


def obtener_por_red(db: Session, marca_id: UUID, red_social: str) -> Optional[CuentasSocialesMkt]:
    """Retorna el objeto ORM completo (con token encriptado) para uso interno."""
    return db.query(CuentasSocialesMkt).filter(
        CuentasSocialesMkt.marca_id == marca_id,
        CuentasSocialesMkt.red_social == red_social,
        CuentasSocialesMkt.activa == True,  # noqa: E712
    ).first()


def desactivar(db: Session, cuenta_id: UUID, marca_id: UUID) -> bool:
    """Desactiva una cuenta social. Retorna True si existía."""
    obj = db.query(CuentasSocialesMkt).filter(
        CuentasSocialesMkt.id == cuenta_id,
        CuentasSocialesMkt.marca_id == marca_id,
    ).first()
    if not obj:
        return False
    obj.activa = False
    db.flush()
    return True
