"""Adaptador HTTP para el módulo de Ads."""
from __future__ import annotations

import logging
from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from middleware.error_handler import AppError
from repositories import umbrales_repository
from services import campanas_service, monitoreo_ads_service

logger = logging.getLogger(__name__)


class CrearCampanaRequest(BaseModel):
    nombre: str
    plataforma: str = Field(pattern="^(meta|google)$")
    objetivo: Optional[str] = None
    presupuesto_diario: Decimal
    presupuesto_mensual: Optional[Decimal] = None


class PausarRequest(BaseModel):
    motivo: str = "manual"


class ActualizarUmbralesRequest(BaseModel):
    cpa_maximo: Optional[Decimal] = None
    roas_minimo: Optional[Decimal] = None
    gasto_diario_maximo: Optional[Decimal] = None


class VerificarUmbralesRequest(BaseModel):
    modo: str = Field(default="copilot", pattern="^(copilot|autopilot)$")
    access_token: str = "mock"


def _marca(x_marca_id: Optional[str]) -> UUID:
    if not x_marca_id:
        raise AppError("Header X-Marca-ID es requerido", "MISSING_MARCA_ID", 400)
    try:
        return UUID(x_marca_id)
    except ValueError:
        raise AppError("X-Marca-ID debe ser un UUID válido", "INVALID_MARCA_ID", 400)


class AdsController:
    def __init__(self, db: Session):
        self.db = db

    def listar_campanas(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        marca_id = _marca(x_marca_id)
        items = campanas_service.listar(self.db, marca_id)
        return {"data": items, "count": len(items)}

    def crear_campana(self, body: CrearCampanaRequest, x_marca_id: Optional[str],
                      current_user: dict) -> dict:
        marca_id = _marca(x_marca_id)
        return campanas_service.crear_campana(
            self.db, marca_id, UUID(current_user["cliente_id"]),
            body.model_dump(), UUID(current_user["sub"]),
        )

    def obtener_campana(self, campana_id: UUID, x_marca_id: Optional[str],
                        current_user: dict) -> dict:
        marca_id = _marca(x_marca_id)
        return campanas_service.obtener_con_metricas(self.db, campana_id, marca_id)

    def aprobar_campana(self, campana_id: UUID, x_marca_id: Optional[str],
                        current_user: dict) -> dict:
        marca_id = _marca(x_marca_id)
        return campanas_service.aprobar_campana(
            self.db, campana_id, marca_id, UUID(current_user["sub"]), access_token="mock",
        )

    def pausar_campana(self, campana_id: UUID, body: PausarRequest,
                       x_marca_id: Optional[str], current_user: dict) -> dict:
        marca_id = _marca(x_marca_id)
        return campanas_service.pausar_campana(
            self.db, campana_id, marca_id, UUID(current_user["sub"]),
            access_token="mock", motivo=body.motivo,
        )

    def obtener_umbrales(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        marca_id = _marca(x_marca_id)
        return umbrales_repository.obtener_o_crear(self.db, marca_id)

    def actualizar_umbrales(self, body: ActualizarUmbralesRequest,
                            x_marca_id: Optional[str], current_user: dict) -> dict:
        marca_id = _marca(x_marca_id)
        data = {k: v for k, v in body.model_dump().items() if v is not None}
        return umbrales_repository.actualizar(self.db, marca_id, data)

    def verificar_umbrales(self, body: VerificarUmbralesRequest,
                           x_marca_id: Optional[str], current_user: dict) -> dict:
        marca_id = _marca(x_marca_id)
        alertas = monitoreo_ads_service.verificar_umbrales(
            self.db, marca_id, UUID(current_user["sub"]),
            body.access_token, body.modo,
        )
        return {"alertas": alertas, "count": len(alertas)}
