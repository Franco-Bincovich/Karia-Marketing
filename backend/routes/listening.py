"""Rutas de Social Listening — M09."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.orm import Session

from controllers.listening_controller import ListeningController
from integrations.database import get_db
from middleware.auth import get_current_user

router = APIRouter(prefix="/api/listening", tags=["listening"])


def _ctrl(db: Session = Depends(get_db)) -> ListeningController:
    return ListeningController(db)


@router.post("/escanear")
def escanear(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: ListeningController = Depends(_ctrl),
):
    """Ejecuta búsqueda de menciones nuevas via Claude web search."""
    return ctrl.escanear(x_marca_id, current_user)


@router.get("/menciones")
def menciones(
    x_marca_id: Optional[str] = Header(default=None),
    sentimiento: Optional[str] = Query(default=None),
    plataforma: Optional[str] = Query(default=None),
    desde: Optional[str] = Query(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: ListeningController = Depends(_ctrl),
):
    """Lista menciones con filtros opcionales."""
    return ctrl.menciones(x_marca_id, current_user, sentimiento=sentimiento, plataforma=plataforma, desde=desde)


@router.get("/resumen")
def resumen(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: ListeningController = Depends(_ctrl),
):
    """Estadísticas y métricas del listening."""
    return ctrl.resumen(x_marca_id, current_user)


@router.get("/alertas")
def alertas(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: ListeningController = Depends(_ctrl),
):
    """Lista alertas activas de listening."""
    return ctrl.alertas(x_marca_id, current_user)


@router.patch("/menciones/{mencion_id}/procesar")
def procesar(
    mencion_id: UUID,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: ListeningController = Depends(_ctrl),
):
    """Marca una mención como procesada."""
    return ctrl.procesar(mencion_id, x_marca_id, current_user)
