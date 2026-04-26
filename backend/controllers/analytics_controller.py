"""Adaptador HTTP para el módulo de Analytics y Reporting."""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from middleware.error_handler import AppError
from services import analytics_service, reporting_service

logger = logging.getLogger(__name__)


class MetricasQuery(BaseModel):
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None


class KpiToggleRequest(BaseModel):
    activo: bool


class GenerarReporteRequest(BaseModel):
    tipo: str = Field(default="semanal", pattern="^(diario|semanal|mensual)$")


class ConfigReportesRequest(BaseModel):
    frecuencia: Optional[str] = Field(default=None, pattern="^(diario|semanal|mensual)$")
    formatos: Optional[list] = None
    canal_notificacion: Optional[str] = Field(default=None, pattern="^(email|whatsapp|panel|todos)$")
    email_reporte: Optional[str] = None
    whatsapp_reporte: Optional[str] = None
    incluir_comparacion: Optional[bool] = None
    periodo_comparacion: Optional[str] = None


def _marca(x_marca_id: Optional[str]) -> UUID:
    """Extrae y valida marca_id del header."""
    if not x_marca_id:
        raise AppError("Header X-Marca-ID es requerido", "MISSING_MARCA_ID", 400)
    try:
        return UUID(x_marca_id)
    except ValueError:
        raise AppError("X-Marca-ID debe ser un UUID válido", "INVALID_MARCA_ID", 400)


class AnalyticsController:
    def __init__(self, db: Session):
        self.db = db

    def _check_premium(self, current_user: dict, marca_id: UUID):
        """Analytics solo Premium o superadmin."""
        if current_user.get("rol") == "superadmin":
            return
        from models.cliente_models import ClienteMkt, MarcaMkt

        marca = self.db.query(MarcaMkt).filter(MarcaMkt.id == marca_id).first()
        if marca:
            cliente = self.db.query(ClienteMkt).filter(ClienteMkt.id == marca.cliente_id).first()
            if cliente and cliente.plan == "Premium":
                return
        raise AppError("Analytics solo disponible en Premium", "PLAN_LIMIT", 403)

    def dashboard(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        marca_id = _marca(x_marca_id)
        self._check_premium(current_user, marca_id)
        return analytics_service.obtener_dashboard(self.db, marca_id)

    def tendencias(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        marca_id = _marca(x_marca_id)
        self._check_premium(current_user, marca_id)
        return analytics_service.obtener_tendencias(self.db, marca_id)

    def top_contenido(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        marca_id = _marca(x_marca_id)
        self._check_premium(current_user, marca_id)
        items = analytics_service.obtener_top_contenido(self.db, marca_id)
        return {"data": items, "count": len(items)}

    def metricas(self, fecha_inicio: Optional[date], fecha_fin: Optional[date], x_marca_id: Optional[str], current_user: dict) -> dict:
        """Métricas sociales por período."""
        from repositories import metricas_sociales_repository

        fin = fecha_fin or date.today()
        inicio = fecha_inicio or (fin - timedelta(days=30))
        items = metricas_sociales_repository.listar(self.db, _marca(x_marca_id), inicio, fin)
        return {"data": items, "count": len(items)}

    def consolidar(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Consolida métricas del día."""
        return analytics_service.consolidar_metricas(self.db, _marca(x_marca_id), date.today())

    def kpis(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Lista KPIs disponibles y activos."""
        from repositories import kpis_repository

        activos = kpis_repository.obtener_activos(self.db, _marca(x_marca_id))
        disponibles = kpis_repository.listar_todos_disponibles()
        return {"activos": activos, "disponibles": disponibles}

    def toggle_kpi(self, kpi: str, body: KpiToggleRequest, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Activa o desactiva un KPI."""
        from repositories import kpis_repository

        return kpis_repository.activar_desactivar(self.db, _marca(x_marca_id), kpi, body.activo)

    def reportes(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Lista reportes generados."""
        from repositories import reportes_repository

        items = reportes_repository.listar(self.db, _marca(x_marca_id))
        return {"data": items, "count": len(items)}

    def generar_reporte(self, body: GenerarReporteRequest, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Genera un reporte manual."""
        return reporting_service.generar_reporte(self.db, _marca(x_marca_id), body.tipo)

    def alertas(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Lista alertas."""
        from repositories import alertas_repository

        items = alertas_repository.listar(self.db, _marca(x_marca_id))
        return {"data": items, "count": len(items)}

    def leer_alerta(self, alerta_id: UUID, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Marca alerta como leída."""
        from repositories import alertas_repository

        r = alertas_repository.marcar_leida(self.db, alerta_id, _marca(x_marca_id))
        if not r:
            raise AppError("Alerta no encontrada", "NOT_FOUND", 404)
        self.db.commit()
        return r

    def config(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Obtiene configuración de reportes."""
        from repositories import config_reportes_repository

        return config_reportes_repository.obtener_o_crear(self.db, _marca(x_marca_id))

    def actualizar_config(self, body: ConfigReportesRequest, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Actualiza configuración de reportes."""
        from repositories import config_reportes_repository

        data = {k: v for k, v in body.model_dump().items() if v is not None}
        return config_reportes_repository.actualizar(self.db, _marca(x_marca_id), data)
