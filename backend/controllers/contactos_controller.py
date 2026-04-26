"""
Adaptador HTTP para el servicio de contactos.

Extrae marca_id del header X-Marca-ID.
Delega 100% al service — sin lógica de negocio.
"""

import logging
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.orm import Session

from middleware.error_handler import AppError
from services import contactos_service

logger = logging.getLogger(__name__)


# ── Schemas de request ──────────────────────────────────────────────


class BuscarIARequest(BaseModel):
    rubro: str
    ubicacion: str
    cantidad: int = 10
    prompt_personalizado: Optional[str] = None


class GuardarSeleccionRequest(BaseModel):
    contactos: List[dict]


class ContactoManualRequest(BaseModel):
    empresa: str
    nombre: Optional[str] = None
    cargo: Optional[str] = None
    email_empresarial: Optional[str] = None
    email_personal: Optional[str] = None
    telefono_empresa: Optional[str] = None
    telefono_personal: Optional[str] = None
    linkedin_url: Optional[str] = None
    notas: Optional[str] = None


# ── Helpers ─────────────────────────────────────────────────────────


def _get_marca_id(x_marca_id: Optional[str]) -> UUID:
    """Extrae y valida el UUID de marca del header X-Marca-ID."""
    if not x_marca_id:
        raise AppError("Header X-Marca-ID es requerido", "MISSING_MARCA_ID", 400)
    try:
        return UUID(x_marca_id)
    except ValueError:
        raise AppError("X-Marca-ID debe ser un UUID válido", "INVALID_MARCA_ID", 400)


# ── Controller ───────────────────────────────────────────────────────


class ContactosController:
    """Convierte requests HTTP en llamadas al contactos_service."""

    def __init__(self, db: Session):
        self.db = db

    def listar(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Retorna los contactos de la marca activa."""
        marca_id = _get_marca_id(x_marca_id)
        _assert_acceso(current_user, marca_id)
        contactos = contactos_service.listar(self.db, marca_id)
        return {"data": contactos, "count": len(contactos)}

    def buscar_ia(self, body: BuscarIARequest, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Busca prospectos con IA — no persiste."""
        marca_id = _get_marca_id(x_marca_id)
        _assert_acceso(current_user, marca_id)
        resultados = contactos_service.buscar_con_ia(
            db=self.db,
            marca_id=marca_id,
            rubro=body.rubro,
            ubicacion=body.ubicacion,
            cantidad=body.cantidad,
            prompt_personalizado=body.prompt_personalizado,
        )
        return {"data": resultados, "count": len(resultados)}

    def guardar_seleccion(self, body: GuardarSeleccionRequest, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Guarda la selección de contactos encontrados por IA."""
        marca_id = _get_marca_id(x_marca_id)
        cliente_id = UUID(current_user["cliente_id"])
        _assert_acceso(current_user, marca_id)
        resultado = contactos_service.guardar_seleccion(self.db, marca_id, cliente_id, body.contactos)
        return {
            "data": resultado["guardados"],
            "omitidos": resultado["omitidos"],
            "message": f"{len(resultado['guardados'])} guardados, {len(resultado['omitidos'])} omitidos por duplicado",
        }

    def agregar_manual(self, body: ContactoManualRequest, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Agrega un contacto manual."""
        marca_id = _get_marca_id(x_marca_id)
        cliente_id = UUID(current_user["cliente_id"])
        _assert_acceso(current_user, marca_id)
        contacto = contactos_service.agregar_manual(self.db, marca_id, cliente_id, body.model_dump())
        return {"data": contacto}

    def eliminar(self, contacto_id: UUID, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Elimina un contacto de la marca."""
        marca_id = _get_marca_id(x_marca_id)
        _assert_acceso(current_user, marca_id)
        contactos_service.eliminar(self.db, contacto_id, marca_id)
        return {"message": "Contacto eliminado"}


def _assert_acceso(current_user: dict, marca_id: UUID) -> None:
    """Superadmin pasa siempre. Admin y subusuario se validan por marca en el service."""
    if not current_user:
        raise AppError("No autenticado", "UNAUTHORIZED", 401)
