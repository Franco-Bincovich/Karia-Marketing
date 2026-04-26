"""Adaptador HTTP para el módulo de Agentes IA."""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.orm import Session

from middleware.error_handler import AppError
from services import agentes_service as svc


class ActualizarAgenteRequest(BaseModel):
    activo: Optional[bool] = None
    modo: Optional[str] = None
    system_prompt: Optional[str] = None


def _marca(x_marca_id: Optional[str]) -> UUID:
    if not x_marca_id:
        raise AppError("Header X-Marca-ID es requerido", "MISSING_MARCA_ID", 400)
    try:
        return UUID(x_marca_id)
    except ValueError:
        raise AppError("X-Marca-ID debe ser un UUID válido", "INVALID_MARCA_ID", 400)


class AgentesController:
    def __init__(self, db: Session):
        self.db = db

    def listar(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        marca_id = _marca(x_marca_id)
        rol = current_user.get("rol", "")
        items = svc.obtener_config(self.db, marca_id, rol=rol)
        return {"data": items, "count": len(items)}

    def actualizar(self, nombre: str, body: ActualizarAgenteRequest, x_marca_id: Optional[str], current_user: dict) -> dict:
        marca_id = _marca(x_marca_id)
        rol = current_user.get("rol", "")
        return svc.actualizar_config(
            self.db,
            marca_id,
            nombre,
            activo=body.activo,
            modo=body.modo,
            system_prompt=body.system_prompt,
            rol=rol,
        )

    def ejecutar(self, nombre: str, x_marca_id: Optional[str], current_user: dict) -> dict:
        marca_id = _marca(x_marca_id)
        rol = current_user.get("rol", "")
        return svc.ejecutar_agente(self.db, marca_id, nombre, rol=rol)
