"""Rutas de Automatizaciones — M10."""

from typing import Optional

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from controllers.automatizaciones_controller import AutomatizacionesController
from integrations.database import get_db
from middleware.auth import get_current_user

router = APIRouter(prefix="/api/automatizaciones", tags=["automatizaciones"])


def _ctrl(db: Session = Depends(get_db)) -> AutomatizacionesController:
    return AutomatizacionesController(db)


@router.get("")
def listar(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: AutomatizacionesController = Depends(_ctrl),
):
    """Lista las 5 automatizaciones de la marca activa."""
    return ctrl.listar(x_marca_id, current_user)


@router.patch("/{tipo}/activar")
def activar(
    tipo: str,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: AutomatizacionesController = Depends(_ctrl),
):
    """Activa una automatización."""
    return ctrl.activar(tipo, x_marca_id, current_user)


@router.patch("/{tipo}/desactivar")
def desactivar(
    tipo: str,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: AutomatizacionesController = Depends(_ctrl),
):
    """Desactiva una automatización."""
    return ctrl.desactivar(tipo, x_marca_id, current_user)


@router.post("/{tipo}/ejecutar")
def ejecutar(
    tipo: str,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: AutomatizacionesController = Depends(_ctrl),
):
    """Ejecuta manualmente una automatización."""
    return ctrl.ejecutar(tipo, x_marca_id, current_user)
