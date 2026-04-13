"""
Servicio de calendario editorial y publicación en redes sociales.

Maneja la creación de eventos, publicación inmediata con reintentos
y actualización de estados. Los reintentos respetan el límite de 3 intentos
con 5 minutos de espera entre cada uno.
"""

import logging
import time
from uuid import UUID

from sqlalchemy.orm import Session

from integrations import meta_client, linkedin_client
from middleware.error_handler import AppError
from repositories import calendario_repository as repo
from repositories import cuentas_sociales_repository as cuentas_repo
from repositories import publicaciones_repository as pub_repo

logger = logging.getLogger(__name__)

MAX_INTENTOS = 3
RETRY_DELAY_SEG = 300  # 5 minutos — en tests sobreescribir este valor


def crear_evento(db: Session, marca_id: UUID, cliente_id: UUID, evento_data: dict) -> dict:
    """
    Crea un evento en el calendario editorial de una marca.

    Returns:
        Dict del evento creado con estado 'programado'
    """
    data = {**evento_data, "marca_id": marca_id, "cliente_id": cliente_id}
    resultado = repo.crear_evento(db, data)
    db.commit()
    return resultado


def listar_mes(db: Session, marca_id: UUID, mes: int, anio: int) -> list[dict]:
    """Lista los eventos del calendario para el mes y año indicados."""
    return repo.listar(db, marca_id, mes, anio)


def eliminar_evento(db: Session, evento_id: UUID, marca_id: UUID) -> bool:
    """
    Elimina un evento del calendario verificando pertenencia a la marca.

    Raises:
        AppError 404 si el evento no existe
    """
    eliminado = repo.eliminar(db, evento_id, marca_id)
    if not eliminado:
        raise AppError("Evento no encontrado", "NOT_FOUND", 404)
    db.commit()
    return True


def publicar_ahora(db: Session, evento_id: UUID, marca_id: UUID) -> dict:
    """
    Publica inmediatamente el contenido de un evento en la red social correspondiente.

    Reintenta hasta MAX_INTENTOS veces con RETRY_DELAY_SEG entre intentos.
    Registra el resultado en publicaciones_mkt y actualiza el estado del calendario.

    Returns:
        Dict de la publicación creada

    Raises:
        AppError 404 si el evento no existe
        AppError 400 si la red social no tiene cuenta conectada
        AppError 502 si todos los intentos fallan
    """
    evento = repo.obtener(db, evento_id, marca_id)
    if not evento:
        raise AppError("Evento no encontrado", "NOT_FOUND", 404)

    cuenta = cuentas_repo.obtener_por_red(db, marca_id, evento.red_social)
    if not cuenta:
        raise AppError(
            f"No hay cuenta activa de {evento.red_social} para esta marca",
            "NO_SOCIAL_ACCOUNT", 400,
        )

    from utils.security import decrypt_token
    access_token = decrypt_token(cuenta.access_token_encrypted or "mock")
    account_id = cuenta.account_id_externo or "mock"

    ultimo_error = None
    for intento in range(1, MAX_INTENTOS + 1):
        try:
            resultado = _llamar_api(evento.red_social, access_token, account_id, evento)
            pub = pub_repo.crear(db, {
                "marca_id": marca_id,
                "calendario_id": evento.id,
                "contenido_id": evento.contenido_id,
                "red_social": evento.red_social,
                "post_id_externo": resultado["post_id_externo"],
                "url_publicacion": resultado["url_publicacion"],
                "copy_publicado": evento.descripcion,
                "estado": "publicado",
                "intentos": intento,
            })
            repo.actualizar_estado(db, evento.id, "publicado")
            db.commit()
            logger.info(f"[calendario_service] publicado en intento {intento} — {evento.red_social}")
            return pub
        except Exception as exc:
            ultimo_error = str(exc)
            logger.warning(f"[calendario_service] intento {intento} fallido: {ultimo_error}")
            if intento < MAX_INTENTOS:
                time.sleep(RETRY_DELAY_SEG)

    pub = pub_repo.crear(db, {
        "marca_id": marca_id, "calendario_id": evento.id,
        "red_social": evento.red_social, "estado": "fallido",
        "intentos": MAX_INTENTOS, "error_detalle": ultimo_error,
    })
    repo.actualizar_estado(db, evento.id, "fallido")
    db.commit()
    raise AppError(f"Publicación fallida tras {MAX_INTENTOS} intentos: {ultimo_error}", "PUBLISH_FAILED", 502)


def _llamar_api(red_social: str, access_token: str, account_id: str, evento) -> dict:
    """Despacha la llamada al cliente correcto según la red social."""
    if red_social == "instagram":
        return meta_client.publicar_instagram(access_token, account_id, evento.descripcion or "")
    if red_social == "facebook":
        return meta_client.publicar_facebook(access_token, account_id, evento.descripcion or "")
    if red_social == "linkedin":
        return linkedin_client.publicar_linkedin(access_token, account_id, evento.descripcion or "")
    raise AppError(f"Red social {red_social!r} no soportada", "UNSUPPORTED_NETWORK", 400)
