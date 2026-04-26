"""Adaptador HTTP para el servicio de calendario editorial."""

import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.orm import Session

from middleware.error_handler import AppError
from services import calendario_service as svc

logger = logging.getLogger(__name__)


class CrearEventoRequest(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    red_social: str
    formato: str
    fecha_programada: datetime
    contenido_id: Optional[UUID] = None


class ProgramarManualRequest(BaseModel):
    red_social: str
    copy_text: str
    fecha_hora: str
    formato: str = "post"
    imagen_url: Optional[str] = None
    imagenes_urls: Optional[list] = None


def _marca(x_marca_id: Optional[str]) -> UUID:
    if not x_marca_id:
        raise AppError("Header X-Marca-ID es requerido", "MISSING_MARCA_ID", 400)
    try:
        return UUID(x_marca_id)
    except ValueError:
        raise AppError("X-Marca-ID debe ser un UUID válido", "INVALID_MARCA_ID", 400)


class CalendarioController:
    def __init__(self, db: Session):
        self.db = db

    def listar(self, x_marca_id: Optional[str], mes: int, anio: int, current_user: dict) -> dict:
        """Lista eventos del calendario para el mes y año indicados."""
        marca_id = _marca(x_marca_id)
        items = svc.listar_mes(self.db, marca_id, mes, anio)
        return {"data": items, "count": len(items)}

    def crear_evento(self, body: CrearEventoRequest, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Crea un evento en el calendario editorial."""
        marca_id = _marca(x_marca_id)
        cliente_id = UUID(current_user["cliente_id"])
        return svc.crear_evento(self.db, marca_id, cliente_id, body.model_dump())

    def eliminar_evento(self, evento_id: UUID, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Elimina un evento del calendario."""
        marca_id = _marca(x_marca_id)
        svc.eliminar_evento(self.db, evento_id, marca_id)
        return {"message": "Evento eliminado"}

    def programar_manual(self, body: "ProgramarManualRequest", x_marca_id: Optional[str], current_user: dict) -> dict:
        """Programa publicación manual con fecha/hora exacta."""
        marca_id = _marca(x_marca_id)
        return svc.programar_manual(
            self.db,
            marca_id,
            body.red_social,
            body.copy_text,
            body.fecha_hora,
            formato=body.formato,
            imagen_url=body.imagen_url,
            imagenes_urls=body.imagenes_urls,
        )

    def publicar_ahora(self, evento_id: UUID, x_marca_id: Optional[str], current_user: dict) -> dict:
        """
        Publica inmediatamente el evento en la red social correspondiente.
        Reintenta hasta 3 veces con 5 minutos entre intentos si falla.
        """
        marca_id = _marca(x_marca_id)
        return svc.publicar_ahora(self.db, evento_id, marca_id)
