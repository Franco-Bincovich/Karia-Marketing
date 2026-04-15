"""Adaptador HTTP para Automatizaciones."""

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from middleware.error_handler import AppError
from services import automatizaciones_service as svc


def _marca(x_marca_id: Optional[str]) -> UUID:
    if not x_marca_id:
        raise AppError("Header X-Marca-ID es requerido", "MISSING_MARCA_ID", 400)
    try:
        return UUID(x_marca_id)
    except ValueError:
        raise AppError("X-Marca-ID debe ser un UUID válido", "INVALID_MARCA_ID", 400)


class AutomatizacionesController:
    def __init__(self, db: Session):
        self.db = db

    def listar(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        items = svc.listar(self.db, _marca(x_marca_id))
        return {"data": items, "count": len(items)}

    def activar(self, tipo: str, x_marca_id: Optional[str], current_user: dict) -> dict:
        return svc.activar(self.db, _marca(x_marca_id), tipo)

    def desactivar(self, tipo: str, x_marca_id: Optional[str], current_user: dict) -> dict:
        return svc.desactivar(self.db, _marca(x_marca_id), tipo)

    def ejecutar(self, tipo: str, x_marca_id: Optional[str], current_user: dict) -> dict:
        return svc.ejecutar_ahora(self.db, _marca(x_marca_id), tipo)
