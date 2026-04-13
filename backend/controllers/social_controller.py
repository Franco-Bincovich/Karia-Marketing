"""Adaptador HTTP para publicaciones y cuentas sociales."""

import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.orm import Session

from middleware.error_handler import AppError
from repositories import publicaciones_repository as pub_repo
from services import cuentas_sociales_service as cuentas_svc
from services import social_monitoring_service as monitor_svc

logger = logging.getLogger(__name__)


class ConectarCuentaRequest(BaseModel):
    nombre_cuenta: str
    account_id_externo: Optional[str] = None
    access_token: str
    token_expires_at: Optional[datetime] = None


def _marca(x_marca_id: Optional[str]) -> UUID:
    if not x_marca_id:
        raise AppError("Header X-Marca-ID es requerido", "MISSING_MARCA_ID", 400)
    try:
        return UUID(x_marca_id)
    except ValueError:
        raise AppError("X-Marca-ID debe ser un UUID válido", "INVALID_MARCA_ID", 400)


class SocialController:
    def __init__(self, db: Session):
        self.db = db

    def listar_cuentas(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Lista las cuentas sociales conectadas a la marca (sin exponer tokens)."""
        marca_id = _marca(x_marca_id)
        items = cuentas_svc.listar_cuentas(self.db, marca_id)
        return {"data": items, "count": len(items)}

    def conectar_cuenta(
        self, red_social: str, body: ConectarCuentaRequest,
        x_marca_id: Optional[str], current_user: dict,
    ) -> dict:
        """
        Conecta o actualiza una cuenta social para la marca.
        El access_token se encripta con Fernet antes de persistir.
        """
        marca_id = _marca(x_marca_id)
        return cuentas_svc.conectar_cuenta(self.db, marca_id, red_social, body.model_dump())

    def desconectar_cuenta(self, cuenta_id: UUID, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Desactiva una cuenta social (soft delete)."""
        marca_id = _marca(x_marca_id)
        cuentas_svc.desconectar_cuenta(self.db, cuenta_id, marca_id)
        return {"message": "Cuenta desconectada"}

    def listar_publicaciones(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Lista las publicaciones realizadas por la marca."""
        marca_id = _marca(x_marca_id)
        items = pub_repo.listar(self.db, marca_id)
        return {"data": items, "count": len(items)}

    def monitorear(self, publicacion_id: UUID, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Obtiene métricas de las 2hs post-publicación y detecta engagement bajo."""
        marca_id = _marca(x_marca_id)
        return monitor_svc.monitorear_publicacion(self.db, publicacion_id, marca_id)
