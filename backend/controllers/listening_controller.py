"""Adaptador HTTP para Social Listening."""

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from middleware.error_handler import AppError
from services import listening_service as svc


def _marca(x_marca_id: Optional[str]) -> UUID:
    if not x_marca_id:
        raise AppError("Header X-Marca-ID es requerido", "MISSING_MARCA_ID", 400)
    try:
        return UUID(x_marca_id)
    except ValueError:
        raise AppError("X-Marca-ID debe ser un UUID válido", "INVALID_MARCA_ID", 400)


class ListeningController:
    def __init__(self, db: Session):
        self.db = db

    def escanear(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        return svc.buscar_menciones(self.db, _marca(x_marca_id))

    def menciones(self, x_marca_id: Optional[str], current_user: dict,
                  sentimiento: Optional[str] = None, plataforma: Optional[str] = None,
                  desde: Optional[str] = None) -> dict:
        items = svc.listar_menciones(
            self.db, _marca(x_marca_id),
            sentimiento=sentimiento, plataforma=plataforma, desde=desde,
        )
        return {"data": items, "count": len(items)}

    def resumen(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        return svc.obtener_resumen(self.db, _marca(x_marca_id))

    def alertas(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        items = svc.listar_alertas(self.db, _marca(x_marca_id))
        return {"data": items, "count": len(items)}

    def procesar(self, mencion_id: UUID, x_marca_id: Optional[str], current_user: dict) -> dict:
        return svc.marcar_procesada(self.db, mencion_id)
