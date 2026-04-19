"""Rutas del módulo de Estrategia IA — M08."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from controllers.estrategia_controller import EstrategiaController, PlanContenidoRequest
from integrations.database import get_db
from middleware.auth import get_current_user

router = APIRouter(prefix="/api/estrategia", tags=["estrategia"])


def _ctrl(db: Session = Depends(get_db)) -> EstrategiaController:
    return EstrategiaController(db)


@router.post("/analizar-competencia")
def analizar_competencia(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: EstrategiaController = Depends(_ctrl),
):
    """Análisis de competidores con Claude + web search."""
    return ctrl.analizar_competencia(x_marca_id, current_user)


@router.post("/plan-contenido")
def plan_contenido(
    body: PlanContenidoRequest,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: EstrategiaController = Depends(_ctrl),
):
    """Genera plan de contenido (diario/semanal/mensual)."""
    return ctrl.plan_contenido(body, x_marca_id, current_user)


@router.post("/plan-contenido/{plan_id}/activar")
def activar_plan(
    plan_id: UUID,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: EstrategiaController = Depends(_ctrl),
):
    """Activa un plan como el plan vigente de la marca."""
    return ctrl.activar_plan(plan_id, x_marca_id, current_user)


@router.get("/plan-activo")
def plan_activo(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: EstrategiaController = Depends(_ctrl),
):
    """Retorna el plan de contenido activo."""
    return ctrl.plan_activo(x_marca_id, current_user)


@router.get("/sugerencias")
def sugerencias(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: EstrategiaController = Depends(_ctrl),
):
    """Lista sugerencias estratégicas activas."""
    return ctrl.sugerencias(x_marca_id, current_user)


@router.post("/sugerencias")
def generar_sugerencias(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: EstrategiaController = Depends(_ctrl),
):
    """Genera nuevas sugerencias estratégicas."""
    return ctrl.generar_sugerencias(x_marca_id, current_user)


@router.patch("/sugerencias/{estrategia_id}/implementada")
def marcar_implementada(
    estrategia_id: UUID,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: EstrategiaController = Depends(_ctrl),
):
    """Marca una sugerencia como implementada."""
    return ctrl.marcar_implementada(estrategia_id, x_marca_id, current_user)
