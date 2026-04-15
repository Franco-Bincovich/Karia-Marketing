"""Adaptador HTTP para el módulo de Estrategia."""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.orm import Session

from middleware.error_handler import AppError
from services import estrategia_service as svc


class PlanContenidoRequest(BaseModel):
    periodo: str = "semanal"


def _marca(x_marca_id: Optional[str]) -> UUID:
    if not x_marca_id:
        raise AppError("Header X-Marca-ID es requerido", "MISSING_MARCA_ID", 400)
    try:
        return UUID(x_marca_id)
    except ValueError:
        raise AppError("X-Marca-ID debe ser un UUID válido", "INVALID_MARCA_ID", 400)


class EstrategiaController:
    def __init__(self, db: Session):
        self.db = db

    def analizar_competencia(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        return svc.analizar_competencia(self.db, _marca(x_marca_id))

    def plan_contenido(self, body: PlanContenidoRequest,
                       x_marca_id: Optional[str], current_user: dict) -> dict:
        return svc.generar_plan_contenido(self.db, _marca(x_marca_id), periodo=body.periodo)

    def sugerencias(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        items = svc.listar_sugerencias(self.db, _marca(x_marca_id))
        return {"data": items, "count": len(items)}

    def generar_sugerencias(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        return svc.sugerir_acciones(self.db, _marca(x_marca_id))

    def marcar_implementada(self, estrategia_id: UUID,
                            x_marca_id: Optional[str], current_user: dict) -> dict:
        return svc.marcar_implementada(self.db, _marca(x_marca_id), estrategia_id)
