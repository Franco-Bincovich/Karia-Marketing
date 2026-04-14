"""Rutas del módulo Analytics y Reporting."""
from __future__ import annotations

from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.orm import Session

from controllers.analytics_controller import (
    AnalyticsController, ConfigReportesRequest,
    GenerarReporteRequest, KpiToggleRequest,
)
from integrations.database import get_db
from middleware.auth import get_current_user

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


def _ctrl(db: Session = Depends(get_db)) -> AnalyticsController:
    return AnalyticsController(db)


@router.get("/dashboard")
def dashboard(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: AnalyticsController = Depends(_ctrl),
):
    """Datos del dashboard con KPIs, progreso y métricas."""
    return ctrl.dashboard(x_marca_id, current_user)


@router.get("/metricas")
def metricas(
    fecha_inicio: Optional[date] = Query(default=None),
    fecha_fin: Optional[date] = Query(default=None),
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: AnalyticsController = Depends(_ctrl),
):
    """Métricas sociales por período."""
    return ctrl.metricas(fecha_inicio, fecha_fin, x_marca_id, current_user)


@router.post("/consolidar")
def consolidar(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: AnalyticsController = Depends(_ctrl),
):
    """Consolida métricas de todos los canales para hoy."""
    return ctrl.consolidar(x_marca_id, current_user)


@router.get("/kpis")
def kpis(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: AnalyticsController = Depends(_ctrl),
):
    """Lista KPIs disponibles y activos de la marca."""
    return ctrl.kpis(x_marca_id, current_user)


@router.patch("/kpis/{kpi}")
def toggle_kpi(
    kpi: str,
    body: KpiToggleRequest,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: AnalyticsController = Depends(_ctrl),
):
    """Activa o desactiva un KPI para la marca."""
    return ctrl.toggle_kpi(kpi, body, x_marca_id, current_user)


@router.get("/reportes")
def reportes(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: AnalyticsController = Depends(_ctrl),
):
    """Lista reportes generados."""
    return ctrl.reportes(x_marca_id, current_user)


@router.post("/reportes/generar")
def generar_reporte(
    body: GenerarReporteRequest = GenerarReporteRequest(),
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: AnalyticsController = Depends(_ctrl),
):
    """Genera un reporte manual del período configurado."""
    return ctrl.generar_reporte(body, x_marca_id, current_user)


@router.get("/alertas")
def alertas(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: AnalyticsController = Depends(_ctrl),
):
    """Lista alertas de la marca."""
    return ctrl.alertas(x_marca_id, current_user)


@router.patch("/alertas/{alerta_id}/leer")
def leer_alerta(
    alerta_id: UUID,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: AnalyticsController = Depends(_ctrl),
):
    """Marca una alerta como leída."""
    return ctrl.leer_alerta(alerta_id, x_marca_id, current_user)


@router.get("/config")
def config(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: AnalyticsController = Depends(_ctrl),
):
    """Obtiene configuración de reportes de la marca."""
    return ctrl.config(x_marca_id, current_user)


@router.patch("/config")
def actualizar_config(
    body: ConfigReportesRequest,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: AnalyticsController = Depends(_ctrl),
):
    """Actualiza la configuración de reportes."""
    return ctrl.actualizar_config(body, x_marca_id, current_user)
