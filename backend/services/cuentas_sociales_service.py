"""
Servicio de gestión de cuentas sociales conectadas a una marca.

Los access tokens se encriptan con Fernet antes de persistir y
nunca se exponen en las respuestas de la API.
"""

import logging
from uuid import UUID

from sqlalchemy.orm import Session

from middleware.error_handler import AppError
from repositories import cuentas_sociales_repository as repo
from utils.security import encrypt_token

logger = logging.getLogger(__name__)


def conectar_cuenta(db: Session, marca_id: UUID, red_social: str, account_data: dict) -> dict:
    """
    Conecta o actualiza una cuenta social para una marca.

    El access_token se encripta con Fernet antes de persistir.
    Nunca se loguea ni se retorna el token en texto plano.

    Args:
        marca_id: Marca a la que pertenece la cuenta
        red_social: Red social (instagram, facebook, linkedin, etc.)
        account_data: Dict con nombre_cuenta, account_id_externo,
                      access_token (texto plano), token_expires_at (opcional)

    Returns:
        Dict de la cuenta sin exponer el token encriptado
    """
    raw_token = account_data.pop("access_token", None)
    if not raw_token:
        raise AppError("El access_token es requerido", "MISSING_TOKEN", 400)

    encrypted = encrypt_token(raw_token)
    # raw_token sale de memoria — no se loguea en ningún momento

    data = {
        **account_data,
        "marca_id": marca_id,
        "red_social": red_social,
        "access_token_encrypted": encrypted,
        "activa": True,
    }

    resultado = repo.crear_o_actualizar(db, data)
    db.commit()
    logger.info(f"[cuentas_service] cuenta conectada — marca={marca_id}, red={red_social}")
    return resultado


def listar_cuentas(db: Session, marca_id: UUID) -> list[dict]:
    """
    Lista las cuentas sociales de una marca.
    Los tokens encriptados nunca se incluyen en la respuesta.
    """
    return repo.listar(db, marca_id)


def desconectar_cuenta(db: Session, cuenta_id: UUID, marca_id: UUID) -> bool:
    """
    Desactiva una cuenta social (soft delete).

    Raises:
        AppError 404 si la cuenta no existe o no pertenece a la marca
    """
    desactivada = repo.desactivar(db, cuenta_id, marca_id)
    if not desactivada:
        raise AppError("Cuenta no encontrada", "NOT_FOUND", 404)
    db.commit()
    logger.info(f"[cuentas_service] cuenta desconectada — id={cuenta_id}")
    return True
