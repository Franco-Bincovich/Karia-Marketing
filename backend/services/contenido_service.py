"""
Servicio de generación de contenido IA — Módulo 3.

Orquesta claude_client + repositorios para generar, listar y gestionar
piezas de contenido con variantes A/B. El feedback se delega a
contenido_feedback_service para respetar el límite de 150 líneas.
"""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from integrations import claude_client
from middleware.error_handler import AppError
from repositories import aprendizaje_repository as ap_repo
from repositories import contenido_repository as repo
from repositories import templates_repository as tpl_repo

logger = logging.getLogger(__name__)


def generar_contenido(
    db: Session,
    marca_id: UUID,
    cliente_id: UUID,
    red_social: str,
    formato: str,
    objetivo: str,
    tono: str,
    tema: str,
    memoria_marca: str,
    modo: str = "copilot",
) -> dict:
    """
    Genera variantes A/B con Claude y persiste la pieza de contenido.

    En modo 'copilot' el estado inicial es 'pendiente_aprobacion'.
    En modo 'autopilot' el estado inicial es 'aprobado'.

    Returns:
        Dict con la pieza de contenido creada y sus variantes A/B
    """
    logger.info(f"[contenido_service] generar — marca={marca_id}, {red_social}/{formato}")

    prefs = ap_repo.obtener_preferencias(db, marca_id)
    if prefs["tono_preferido"] and not tono:
        tono = prefs["tono_preferido"]
        logger.debug(f"[contenido_service] usando tono aprendido: {tono!r}")

    resultado = claude_client.generar_contenido_ia(
        red_social=red_social, formato=formato, objetivo=objetivo,
        tono=tono, tema=tema, memoria_marca=memoria_marca,
    )

    estado = "aprobado" if modo == "autopilot" else "pendiente_aprobacion"
    data = {
        "marca_id": marca_id, "cliente_id": cliente_id,
        "red_social": red_social, "formato": formato,
        "objetivo": objetivo, "tono": tono, "tema": tema,
        "copy_a": resultado["copy_a"], "copy_b": resultado["copy_b"],
        "hashtags_a": resultado.get("hashtags_a"), "hashtags_b": resultado.get("hashtags_b"),
        "estado": estado, "modo": modo,
    }
    contenido = repo.crear(db, data)

    repo.guardar_version(db, UUID(contenido["id"]), {
        "copy_a": resultado["copy_a"], "copy_b": resultado["copy_b"],
        "creado_por": "ia",
    })

    db.commit()
    contenido["variable_testeada"] = resultado.get("variable_testeada")
    return contenido


def listar(db: Session, marca_id: UUID) -> list[dict]:
    """Retorna todo el contenido de una marca ordenado por fecha descendente."""
    return repo.listar(db, marca_id)


def obtener_versiones(db: Session, contenido_id: UUID, marca_id: UUID) -> list[dict]:
    """
    Retorna el historial de versiones de una pieza de contenido.

    Raises:
        AppError 404 si la pieza no existe o no pertenece a la marca
    """
    if not repo.obtener(db, contenido_id, marca_id):
        raise AppError("Contenido no encontrado", "NOT_FOUND", 404)
    return repo.listar_versiones(db, contenido_id)


def crear_template(db: Session, marca_id: UUID, template_data: dict) -> dict:
    """Crea un template reutilizable para una marca."""
    data = {**template_data, "marca_id": marca_id}
    resultado = tpl_repo.crear(db, data)
    db.commit()
    return resultado


def listar_templates(db: Session, marca_id: UUID) -> list[dict]:
    """Lista los templates de una marca ordenados por usos."""
    return tpl_repo.listar(db, marca_id)


def eliminar_template(db: Session, template_id: UUID, marca_id: UUID) -> bool:
    """
    Elimina un template verificando pertenencia a la marca.

    Raises:
        AppError 404 si no existe
    """
    eliminado = tpl_repo.eliminar(db, template_id, marca_id)
    if not eliminado:
        raise AppError("Template no encontrado", "NOT_FOUND", 404)
    db.commit()
    return True
