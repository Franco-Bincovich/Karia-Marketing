"""Rutas del módulo Comunidad y Social Listening."""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from controllers.comunidad_controller import (
    ConfigComunidadRequest, ConfigListeningRequest,
    ComunidadController, MensajeRequest, ResponderRequest,
)
from integrations.database import get_db
from middleware.auth import get_current_user

router = APIRouter(prefix="/api/comunidad", tags=["comunidad"])


def _ctrl(db: Session = Depends(get_db)) -> ComunidadController:
    return ComunidadController(db)


@router.get("/mensajes")
def listar_mensajes(x_marca_id: Optional[str] = Header(default=None),
                    current_user: dict = Depends(get_current_user),
                    ctrl: ComunidadController = Depends(_ctrl)):
    return ctrl.listar_mensajes(x_marca_id, current_user)


@router.get("/mensajes/pendientes")
def mensajes_pendientes(x_marca_id: Optional[str] = Header(default=None),
                        current_user: dict = Depends(get_current_user),
                        ctrl: ComunidadController = Depends(_ctrl)):
    return ctrl.mensajes_pendientes(x_marca_id, current_user)


@router.post("/mensajes")
def recibir_mensaje(body: MensajeRequest,
                    x_marca_id: Optional[str] = Header(default=None),
                    current_user: dict = Depends(get_current_user),
                    ctrl: ComunidadController = Depends(_ctrl)):
    return ctrl.recibir_mensaje(body, x_marca_id, current_user)


@router.post("/mensajes/{msg_id}/responder")
def responder_mensaje(
    msg_id: UUID, body: ResponderRequest,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: ComunidadController = Depends(_ctrl),
):
    """Responde un mensaje manualmente."""
    return ctrl.responder_mensaje(msg_id, body, x_marca_id, current_user)


@router.get("/leads")
def leads(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: ComunidadController = Depends(_ctrl),
):
    """Lista leads detectados en DMs."""
    return ctrl.leads(x_marca_id, current_user)


@router.get("/menciones")
def menciones(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: ComunidadController = Depends(_ctrl),
):
    """Lista menciones de la marca."""
    return ctrl.menciones(x_marca_id, current_user)


@router.get("/menciones/urgentes")
def menciones_urgentes(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: ComunidadController = Depends(_ctrl),
):
    """Lista menciones urgentes."""
    return ctrl.menciones_urgentes(x_marca_id, current_user)


@router.post("/monitorear")
def monitorear(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: ComunidadController = Depends(_ctrl),
):
    """Ejecuta monitoreo de social listening."""
    return ctrl.monitorear(x_marca_id, current_user)


@router.get("/sentimiento")
def sentimiento(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: ComunidadController = Depends(_ctrl),
):
    """Análisis de sentimiento de la marca."""
    return ctrl.sentimiento(x_marca_id, current_user)


@router.get("/config")
def config_comunidad(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: ComunidadController = Depends(_ctrl),
):
    """Obtiene configuración de comunidad."""
    return ctrl.config_comunidad(x_marca_id, current_user)


@router.patch("/config")
def actualizar_config_comunidad(
    body: ConfigComunidadRequest,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: ComunidadController = Depends(_ctrl),
):
    """Actualiza configuración de comunidad."""
    return ctrl.actualizar_config_comunidad(body, x_marca_id, current_user)


@router.get("/config/listening")
def config_listening(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: ComunidadController = Depends(_ctrl),
):
    """Obtiene configuración de listening."""
    return ctrl.config_listening(x_marca_id, current_user)


@router.patch("/config/listening")
def actualizar_config_listening(
    body: ConfigListeningRequest,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: ComunidadController = Depends(_ctrl),
):
    """Actualiza configuración de listening."""
    return ctrl.actualizar_config_listening(body, x_marca_id, current_user)
