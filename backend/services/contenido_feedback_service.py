"""
Servicio de feedback y aprendizaje de contenido — Módulo 3.

Maneja aprobar, rechazar (con regeneración) y editar.
Cada acción registra un evento en aprendizaje_mkt para el motor de mejora continua.
"""

import logging
from uuid import UUID

from sqlalchemy.orm import Session

from integrations import claude_client
from middleware.error_handler import AppError
from repositories import aprendizaje_repository as ap_repo
from repositories import contenido_repository as repo

logger = logging.getLogger(__name__)


def aprobar(db: Session, contenido_id: UUID, marca_id: UUID, variante: str) -> dict:
    """
    Aprueba una pieza de contenido con la variante seleccionada (a o b).

    Registra evento de aprobación en aprendizaje_mkt para autoaprendizaje.

    Args:
        variante: 'a' o 'b'

    Returns:
        Pieza de contenido actualizada

    Raises:
        AppError 404 si no existe
        AppError 400 si la variante es inválida
    """
    if variante not in ("a", "b"):
        raise AppError("La variante debe ser 'a' o 'b'", "INVALID_VARIANTE", 400)

    obj = repo.obtener(db, contenido_id, marca_id)
    if not obj:
        raise AppError("Contenido no encontrado", "NOT_FOUND", 404)

    contenido = repo.actualizar_campos(db, obj, {
        "estado": "aprobado",
        "variante_seleccionada": variante,
    })

    copy_aprobado = obj.copy_a if variante == "a" else obj.copy_b
    ap_repo.registrar(db, {
        "marca_id": marca_id, "contenido_id": contenido_id,
        "tipo": "aprobacion", "red_social": obj.red_social,
        "formato": obj.formato, "tono": obj.tono,
        "copy_final": copy_aprobado,
    })

    db.commit()
    logger.info(f"[feedback_service] aprobado — id={contenido_id}, variante={variante}")
    return contenido


def rechazar(db: Session, contenido_id: UUID, marca_id: UUID, comentario: str) -> dict:
    """
    Rechaza una pieza e incorpora el feedback para regenerar nuevas variantes A/B.

    Flujo:
      1. Marca el contenido como 'rechazado'
      2. Registra el evento en aprendizaje_mkt
      3. Llama a Claude con el feedback como instrucción adicional
      4. Actualiza el contenido con los nuevos copies
      5. Guarda la nueva versión en versiones_contenido_mkt
      6. Devuelve el contenido en estado 'pendiente_aprobacion'

    Returns:
        Pieza de contenido con nuevas variantes A/B lista para re-aprobación
    """
    obj = repo.obtener(db, contenido_id, marca_id)
    if not obj:
        raise AppError("Contenido no encontrado", "NOT_FOUND", 404)

    ap_repo.registrar(db, {
        "marca_id": marca_id, "contenido_id": contenido_id,
        "tipo": "rechazo", "red_social": obj.red_social,
        "formato": obj.formato, "tono": obj.tono,
        "comentario": comentario,
        "copy_original": obj.copy_a,
    })

    logger.info(f"[feedback_service] rechazado — id={contenido_id}, regenerando con feedback")

    nuevo = claude_client.generar_contenido_ia(
        red_social=obj.red_social, formato=obj.formato,
        objetivo=obj.objetivo or "", tono=obj.tono or "",
        tema=obj.tema or "", memoria_marca="",
        feedback_previo=comentario,
    )

    contenido = repo.actualizar_campos(db, obj, {
        "copy_a": nuevo["copy_a"], "copy_b": nuevo["copy_b"],
        "hashtags_a": nuevo.get("hashtags_a"), "hashtags_b": nuevo.get("hashtags_b"),
        "estado": "pendiente_aprobacion",
        "variante_seleccionada": None,
    })

    repo.guardar_version(db, contenido_id, {
        "copy_a": nuevo["copy_a"], "copy_b": nuevo["copy_b"],
        "motivo_rechazo": comentario, "creado_por": "ia",
    })

    db.commit()
    return contenido


def editar(db: Session, contenido_id: UUID, marca_id: UUID, copy_editado: str, variante: str) -> dict:
    """
    Guarda la edición manual del cliente sobre una variante específica.

    Registra el evento de edición en aprendizaje_mkt con copy_original y copy_final
    para que el motor aprenda las preferencias de estilo de la marca.

    Args:
        copy_editado: Texto final editado por el usuario
        variante: 'a' o 'b' — cuál variante se editó

    Returns:
        Pieza de contenido actualizada
    """
    if variante not in ("a", "b"):
        raise AppError("La variante debe ser 'a' o 'b'", "INVALID_VARIANTE", 400)

    obj = repo.obtener(db, contenido_id, marca_id)
    if not obj:
        raise AppError("Contenido no encontrado", "NOT_FOUND", 404)

    copy_original = obj.copy_a if variante == "a" else obj.copy_b
    campo = "copy_a" if variante == "a" else "copy_b"

    contenido = repo.actualizar_campos(db, obj, {campo: copy_editado})

    repo.guardar_version(db, contenido_id, {
        campo: copy_editado, "creado_por": "humano",
    })

    ap_repo.registrar(db, {
        "marca_id": marca_id, "contenido_id": contenido_id,
        "tipo": "edicion", "red_social": obj.red_social,
        "formato": obj.formato, "tono": obj.tono,
        "copy_original": copy_original, "copy_final": copy_editado,
    })

    db.commit()
    logger.info(f"[feedback_service] edicion — id={contenido_id}, variante={variante}")
    return contenido
