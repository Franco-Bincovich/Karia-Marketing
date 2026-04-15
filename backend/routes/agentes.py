"""Rutas del módulo de Agentes IA — Módulo 7."""

from typing import Optional

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from controllers.agentes_controller import ActualizarAgenteRequest, AgentesController
from integrations.database import get_db
from middleware.auth import get_current_user

router = APIRouter(prefix="/api/agentes", tags=["agentes"])


def _ctrl(db: Session = Depends(get_db)) -> AgentesController:
    return AgentesController(db)


@router.get("")
def listar(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: AgentesController = Depends(_ctrl),
):
    """Configuración completa de los 12 agentes para la marca activa."""
    return ctrl.listar(x_marca_id, current_user)


@router.patch("/{nombre}")
def actualizar(
    nombre: str,
    body: ActualizarAgenteRequest,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: AgentesController = Depends(_ctrl),
):
    """Actualiza configuración de un agente (activo, modo, system_prompt)."""
    return ctrl.actualizar(nombre, body, x_marca_id, current_user)


@router.post("/{nombre}/ejecutar")
def ejecutar(
    nombre: str,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: AgentesController = Depends(_ctrl),
):
    """Ejecuta manualmente un agente (modo Copilot — devuelve resultado para aprobar)."""
    return ctrl.ejecutar(nombre, x_marca_id, current_user)
