"""Rutas del módulo Onboarding y Memoria de Marca."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from controllers.onboarding_controller import (
    MemoriaUpdateRequest, OnboardingController, PasoRequest,
)
from integrations.database import get_db
from middleware.auth import get_current_user

router = APIRouter(prefix="/api/onboarding", tags=["onboarding"])


def _ctrl(db: Session = Depends(get_db)) -> OnboardingController:
    return OnboardingController(db)


@router.get("/estado")
def estado(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: OnboardingController = Depends(_ctrl),
):
    """Estado del onboarding con pasos, completitud y memoria."""
    return ctrl.estado(x_marca_id, current_user)


@router.post("/iniciar")
def iniciar(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: OnboardingController = Depends(_ctrl),
):
    """Inicia el proceso de onboarding para una marca."""
    return ctrl.iniciar(x_marca_id, current_user)


@router.post("/paso/{numero}")
def completar_paso(
    numero: int, body: PasoRequest,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: OnboardingController = Depends(_ctrl),
):
    """Completa un paso del onboarding (1-10)."""
    return ctrl.completar_paso(numero, body, x_marca_id, current_user)


@router.get("/memoria")
def obtener_memoria(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: OnboardingController = Depends(_ctrl),
):
    """Obtiene la memoria de marca completa."""
    return ctrl.obtener_memoria(x_marca_id, current_user)


@router.patch("/memoria")
def actualizar_memoria(
    body: MemoriaUpdateRequest,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: OnboardingController = Depends(_ctrl),
):
    """Actualiza la memoria de marca manualmente."""
    return ctrl.actualizar_memoria(body, x_marca_id, current_user)


@router.get("/memoria/agente/{agente}")
def memoria_agente(
    agente: str,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: OnboardingController = Depends(_ctrl),
):
    """Retorna memoria formateada para un agente específico."""
    return ctrl.memoria_agente(agente, x_marca_id, current_user)


@router.post("/memoria/regenerar")
def regenerar_memoria(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: OnboardingController = Depends(_ctrl),
):
    """Regenera la memoria de marca para inyectar en agentes."""
    return ctrl.regenerar_memoria(x_marca_id, current_user)
