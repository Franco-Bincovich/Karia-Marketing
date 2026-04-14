"""Rutas de campañas publicitarias — Módulo 5 Ads."""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from controllers.ads_controller import (
    ActualizarUmbralesRequest, AdsController, CrearCampanaRequest,
    PausarRequest, VerificarUmbralesRequest,
)
from integrations.database import get_db
from middleware.auth import get_current_user

router = APIRouter(prefix="/api/ads", tags=["ads"])


def _ctrl(db: Session = Depends(get_db)) -> AdsController:
    return AdsController(db)


@router.get("/campanas")
def listar_campanas(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: AdsController = Depends(_ctrl),
):
    return ctrl.listar_campanas(x_marca_id, current_user)


@router.post("/campanas")
def crear_campana(
    body: CrearCampanaRequest,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: AdsController = Depends(_ctrl),
):
    return ctrl.crear_campana(body, x_marca_id, current_user)


@router.get("/campanas/{campana_id}")
def obtener_campana(
    campana_id: UUID,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: AdsController = Depends(_ctrl),
):
    return ctrl.obtener_campana(campana_id, x_marca_id, current_user)


@router.post("/campanas/{campana_id}/aprobar")
def aprobar_campana(
    campana_id: UUID,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: AdsController = Depends(_ctrl),
):
    return ctrl.aprobar_campana(campana_id, x_marca_id, current_user)


@router.post("/campanas/{campana_id}/pausar")
def pausar_campana(
    campana_id: UUID,
    body: PausarRequest = PausarRequest(),
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: AdsController = Depends(_ctrl),
):
    return ctrl.pausar_campana(campana_id, body, x_marca_id, current_user)


@router.get("/umbrales")
def obtener_umbrales(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: AdsController = Depends(_ctrl),
):
    return ctrl.obtener_umbrales(x_marca_id, current_user)


@router.patch("/umbrales")
def actualizar_umbrales(
    body: ActualizarUmbralesRequest,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: AdsController = Depends(_ctrl),
):
    return ctrl.actualizar_umbrales(body, x_marca_id, current_user)


@router.post("/verificar-umbrales")
def verificar_umbrales(
    body: VerificarUmbralesRequest = VerificarUmbralesRequest(),
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: AdsController = Depends(_ctrl),
):
    return ctrl.verificar_umbrales(body, x_marca_id, current_user)
