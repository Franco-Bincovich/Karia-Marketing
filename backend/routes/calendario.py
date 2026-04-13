"""Rutas del calendario editorial — Módulo 4."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.orm import Session

from controllers.calendario_controller import CalendarioController, CrearEventoRequest
from integrations.database import get_db
from middleware.auth import get_current_user

router = APIRouter(prefix="/api/calendario", tags=["calendario"])


def _ctrl(db: Session = Depends(get_db)) -> CalendarioController:
    return CalendarioController(db)


@router.get("")
def listar_calendario(
    mes: int = Query(default=datetime.now().month, ge=1, le=12),
    anio: int = Query(default=datetime.now().year, ge=2024),
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: CalendarioController = Depends(_ctrl),
):
    """Lista los eventos del calendario para el mes y año indicados."""
    return ctrl.listar(x_marca_id, mes, anio, current_user)


@router.post("")
def crear_evento(
    body: CrearEventoRequest,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: CalendarioController = Depends(_ctrl),
):
    """Crea un evento programado en el calendario editorial."""
    return ctrl.crear_evento(body, x_marca_id, current_user)


@router.delete("/{evento_id}")
def eliminar_evento(
    evento_id: UUID,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: CalendarioController = Depends(_ctrl),
):
    """Elimina un evento del calendario."""
    return ctrl.eliminar_evento(evento_id, x_marca_id, current_user)


@router.post("/{evento_id}/publicar")
def publicar_ahora(
    evento_id: UUID,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: CalendarioController = Depends(_ctrl),
):
    """
    Publica inmediatamente el evento en la red social.
    Reintenta hasta 3 veces con 5 minutos entre intentos si falla.
    """
    return ctrl.publicar_ahora(evento_id, x_marca_id, current_user)
