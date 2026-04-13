"""Rutas de cuentas sociales y publicaciones — Módulo 4."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Path
from sqlalchemy.orm import Session

from controllers.social_controller import ConectarCuentaRequest, SocialController
from integrations.database import get_db
from middleware.auth import get_current_user

router = APIRouter(prefix="/api/social", tags=["social"])


def _ctrl(db: Session = Depends(get_db)) -> SocialController:
    return SocialController(db)


@router.get("/cuentas")
def listar_cuentas(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: SocialController = Depends(_ctrl),
):
    """Lista las cuentas sociales conectadas a la marca (sin exponer tokens)."""
    return ctrl.listar_cuentas(x_marca_id, current_user)


@router.post("/cuentas/{red_social}")
def conectar_cuenta(
    red_social: str = Path(pattern="^(instagram|facebook|linkedin|tiktok|twitter|youtube)$"),
    body: ConectarCuentaRequest = ...,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: SocialController = Depends(_ctrl),
):
    """
    Conecta o actualiza una cuenta social para la marca.
    El access_token se encripta con Fernet antes de almacenarse.
    """
    return ctrl.conectar_cuenta(red_social, body, x_marca_id, current_user)


@router.delete("/cuentas/{cuenta_id}")
def desconectar_cuenta(
    cuenta_id: UUID,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: SocialController = Depends(_ctrl),
):
    """Desconecta (desactiva) una cuenta social de la marca."""
    return ctrl.desconectar_cuenta(cuenta_id, x_marca_id, current_user)


@router.get("/publicaciones")
def listar_publicaciones(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: SocialController = Depends(_ctrl),
):
    """Lista el historial de publicaciones realizadas por la marca."""
    return ctrl.listar_publicaciones(x_marca_id, current_user)


@router.post("/publicaciones/{publicacion_id}/monitorear")
def monitorear(
    publicacion_id: UUID,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: SocialController = Depends(_ctrl),
):
    """Obtiene métricas de las 2hs post-publicación y detecta engagement bajo."""
    return ctrl.monitorear(publicacion_id, x_marca_id, current_user)
