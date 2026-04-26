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

from integrations import linkedin_client, meta_client
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


def programar_manual(
    db: Session,
    marca_id: UUID,
    red_social: str,
    copy_text: str,
    fecha_hora: str,
    formato: str = "post",
    imagen_url: str = None,
    imagenes_urls: list = None,
) -> dict:
    """Programa una publicación para fecha/hora exacta vía Zernio.
    Para carrusel, recibe imagenes_urls con múltiples imágenes en orden."""
    from datetime import datetime, timezone

    from integrations import zernio_client

    cuenta = cuentas_repo.obtener_por_red(db, marca_id, red_social)
    if not cuenta:
        raise AppError(f"No hay cuenta de {red_social} conectada", "NO_SOCIAL_ACCOUNT", 400)

    import re

    try:
        clean = re.sub(r"\.\d+", "", fecha_hora)  # Remove milliseconds
        clean = clean.replace("Z", "+00:00")  # Python 3.9 compat
        programado_para = datetime.fromisoformat(clean)
        if programado_para.tzinfo is None:
            programado_para = programado_para.replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        raise AppError("Fecha inválida. Usá formato ISO 8601.", "INVALID_DATE", 400)

    if programado_para <= datetime.now(timezone.utc):
        raise AppError("La fecha debe ser futura", "INVALID_DATE", 400)

    is_carrusel = formato == "carrusel" and imagenes_urls and len(imagenes_urls) >= 2
    primera_imagen = imagenes_urls[0] if is_carrusel else imagen_url

    # Instagram requiere imagen obligatoriamente
    if red_social == "instagram" and not primera_imagen and not is_carrusel:
        raise AppError("Seleccioná una imagen antes de programar en Instagram", "NO_IMAGE", 400)

    logger.info("[calendario] programar_manual — red=%s, imagen=%s, carrusel=%s", red_social, bool(primera_imagen), is_carrusel)

    pub_data = {
        "marca_id": marca_id,
        "red_social": red_social,
        "formato": formato,
        "copy_publicado": copy_text,
        "imagen_url": primera_imagen,
        "estado": "programado",
        "programado_para": programado_para,
    }

    pub = pub_repo.crear(db, pub_data)
    db.flush()

    logger.info("[calendario] imagen_url que se envía a Zernio: %s", primera_imagen)
    try:
        result = zernio_client.schedule_post(
            account_id=cuenta.account_id_externo,
            text=copy_text,
            scheduled_at=programado_para,
            image_url=primera_imagen if not is_carrusel else None,
            image_urls=imagenes_urls if is_carrusel else None,
            platform=red_social,
            formato=formato,
        )
        from models.social_models import PublicacionesMkt

        obj = db.query(PublicacionesMkt).filter(PublicacionesMkt.id == pub["id"]).first()
        if obj:
            obj.zernio_post_id = result.get("id")
            db.flush()
            pub = pub_repo._s(obj)
        logger.info(
            "[calendario] programado en Zernio — %s %s a las %s (%s imágenes)",
            formato,
            red_social,
            programado_para,
            len(imagenes_urls) if is_carrusel else 1,
        )
    except Exception as e:
        logger.warning("[calendario] Zernio schedule falló, queda pendiente para automatización: %s", e)
        # Se queda como "programado" en DB — la automatización lo publicará

    db.commit()
    return pub


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
            "NO_SOCIAL_ACCOUNT",
            400,
        )

    if not cuenta.access_token_encrypted:
        raise AppError(
            f"La cuenta de {evento.red_social} no tiene token de acceso. Reconectala desde Redes Sociales.",
            "NO_SOCIAL_TOKEN",
            400,
        )
    if not cuenta.account_id_externo:
        raise AppError(
            f"La cuenta de {evento.red_social} no tiene ID externo. Reconectala desde Redes Sociales.",
            "NO_SOCIAL_ACCOUNT_ID",
            400,
        )

    from utils.security import decrypt_token

    access_token = decrypt_token(cuenta.access_token_encrypted)
    account_id = cuenta.account_id_externo

    ultimo_error = None
    for intento in range(1, MAX_INTENTOS + 1):
        try:
            resultado = _llamar_api(evento.red_social, access_token, account_id, evento)
            pub = pub_repo.crear(
                db,
                {
                    "marca_id": marca_id,
                    "calendario_id": evento.id,
                    "contenido_id": evento.contenido_id,
                    "red_social": evento.red_social,
                    "formato": evento.formato,
                    "post_id_externo": resultado["post_id_externo"],
                    "url_publicacion": resultado["url_publicacion"],
                    "copy_publicado": evento.descripcion,
                    "estado": "publicado",
                    "intentos": intento,
                },
            )
            repo.actualizar_estado(db, evento.id, "publicado")
            db.commit()
            logger.info(f"[calendario_service] publicado en intento {intento} — {evento.red_social}")
            return pub
        except Exception as exc:
            ultimo_error = str(exc)
            logger.warning(f"[calendario_service] intento {intento} fallido: {ultimo_error}")
            if intento < MAX_INTENTOS:
                time.sleep(RETRY_DELAY_SEG)

    pub = pub_repo.crear(
        db,
        {
            "marca_id": marca_id,
            "calendario_id": evento.id,
            "red_social": evento.red_social,
            "estado": "fallido",
            "intentos": MAX_INTENTOS,
            "error_detalle": ultimo_error,
        },
    )
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
