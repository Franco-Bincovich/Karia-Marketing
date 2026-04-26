"""
Servicio de negocio para contactos — Módulo de Prospección.

Orquesta entre el repositorio (datos) y claude_client (IA).
Aplica las reglas de dedup, normalización y aislamiento por marca.
"""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from integrations import claude_client
from middleware.error_handler import AppError
from repositories import contactos_repository as repo

logger = logging.getLogger(__name__)


def _normalizar_confianza(valor) -> int:
    """
    Convierte confianza al rango 0-100 (entero).
    Claude devuelve 0.0-1.0; un contacto manual siempre es 100.
    """
    try:
        f = float(valor)
        return round(f * 100) if f <= 1.0 else round(f)
    except (TypeError, ValueError):
        return 0


def _normalizar_origen(origen: Optional[str]) -> str:
    """Normaliza 'ia' → 'ai' y garantiza un valor válido."""
    if origen == "ia":
        return "ai"
    return origen if origen in ("ai", "manual", "apollo", "apify") else "ai"


def buscar_con_ia(
    db: Session,
    marca_id: UUID,
    rubro: str,
    ubicacion: str,
    cantidad: int,
    prompt_personalizado: Optional[str] = None,
) -> list[dict]:
    """
    Busca prospectos B2B con Claude + web search.

    No persiste — solo retorna los candidatos para que el usuario seleccione.

    Args:
        db: Sesión de base de datos (para leer emails existentes y evitar dup. en UI)
        marca_id: Marca activa del usuario
        rubro: Sector a prospectar
        ubicacion: Ciudad o país de búsqueda
        cantidad: Cantidad de contactos (5-50)
        prompt_personalizado: Instrucción extra opcional

    Returns:
        Lista de prospectos con flag `ya_guardado` si el email ya existe en la marca
    """
    if not rubro or len(rubro.strip()) < 3:
        raise AppError("El rubro debe tener al menos 3 caracteres", "INVALID_PARAMS", 400)
    if not ubicacion or len(ubicacion.strip()) < 2:
        raise AppError("La ubicación es requerida", "INVALID_PARAMS", 400)

    logger.info(f"[contactos_service] buscar_con_ia — marca={marca_id}, rubro={rubro!r}")

    contactos = claude_client.buscar_contactos_ia(
        rubro=rubro.strip(),
        ubicacion=ubicacion.strip(),
        cantidad=cantidad,
        prompt_personalizado=prompt_personalizado,
    )

    emails_existentes = repo.listar_emails_por_marca(db, marca_id)

    for c in contactos:
        email = (c.get("email_empresarial") or "").lower().strip()
        c["ya_guardado"] = email in emails_existentes

    return contactos


def guardar_seleccion(
    db: Session,
    marca_id: UUID,
    cliente_id: UUID,
    contactos: list[dict],
) -> dict:
    """
    Guarda una selección de contactos encontrados por IA.
    Omite duplicados por email_empresarial dentro de la misma marca.

    Returns:
        Dict con listas `guardados` y `omitidos` (emails duplicados)
    """
    if not contactos:
        raise AppError("Debe seleccionar al menos un contacto", "EMPTY_SELECTION", 400)

    emails_existentes = repo.listar_emails_por_marca(db, marca_id)
    a_guardar, omitidos = [], []

    for c in contactos:
        email = (c.get("email_empresarial") or "").lower().strip()
        if email and email in emails_existentes:
            omitidos.append(email)
            logger.debug(f"[contactos_service] duplicado omitido: {email}")
            continue

        a_guardar.append(
            {
                "marca_id": marca_id,
                "cliente_id": cliente_id,
                "nombre": c.get("nombre"),
                "empresa": c.get("empresa", ""),
                "cargo": c.get("cargo"),
                "email_empresarial": email or None,
                "telefono_empresa": c.get("telefono_empresa"),
                "confianza": _normalizar_confianza(c.get("confianza", 0)),
                "origen": _normalizar_origen(c.get("origen")),
            }
        )

    guardados = repo.crear_bulk(db, a_guardar) if a_guardar else []
    db.commit()

    logger.info(f"[contactos_service] guardar_seleccion — {len(guardados)} guardados, {len(omitidos)} omitidos")
    return {"guardados": guardados, "omitidos": omitidos}


def agregar_manual(db: Session, marca_id: UUID, cliente_id: UUID, contacto: dict) -> dict:
    """
    Agrega un contacto cargado manualmente por el usuario.
    Confianza = 100 (dato ingresado por humano).

    Raises:
        AppError 409 si el email ya existe en la marca
    """
    email = (contacto.get("email_empresarial") or "").lower().strip()
    if email and repo.buscar_por_email(db, email, marca_id):
        raise AppError(f"Ya existe un contacto con el email {email}", "DUPLICATE_EMAIL", 409)

    data = {
        "marca_id": marca_id,
        "cliente_id": cliente_id,
        "nombre": contacto.get("nombre"),
        "empresa": contacto.get("empresa", ""),
        "cargo": contacto.get("cargo"),
        "email_empresarial": email or None,
        "email_personal": contacto.get("email_personal"),
        "telefono_empresa": contacto.get("telefono_empresa"),
        "telefono_personal": contacto.get("telefono_personal"),
        "linkedin_url": contacto.get("linkedin_url"),
        "notas": contacto.get("notas"),
        "confianza": 100,
        "origen": "manual",
    }

    resultado = repo.crear(db, data)
    db.commit()
    logger.info(f"[contactos_service] agregar_manual — {email or 'sin email'}")
    return resultado


def listar(db: Session, marca_id: UUID) -> list[dict]:
    """Retorna todos los contactos de una marca."""
    return repo.listar(db, marca_id)


def eliminar(db: Session, contacto_id: UUID, marca_id: UUID) -> bool:
    """
    Elimina un contacto verificando que pertenezca a la marca.

    Raises:
        AppError 404 si el contacto no existe o no pertenece a la marca
    """
    eliminado = repo.eliminar(db, contacto_id, marca_id)
    if not eliminado:
        raise AppError("Contacto no encontrado", "NOT_FOUND", 404)
    db.commit()
    return True
