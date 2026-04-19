"""Rutas de cuentas sociales, publicaciones y Zernio — Módulo 4."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Path, Request
from sqlalchemy.orm import Session

from controllers.social_controller import (
    CompletarOAuthRequest,
    ConectarCuentaRequest,
    IniciarOAuthRequest,
    ProgramarRequest,
    PublicarRequest,
    SocialController,
)
from integrations.database import get_db
from middleware.auth import get_current_user

router = APIRouter(prefix="/api/social", tags=["social"])


def _ctrl(db: Session = Depends(get_db)) -> SocialController:
    return SocialController(db)


# --- OAuth Zernio ---

@router.post("/conectar")
def iniciar_oauth(
    body: IniciarOAuthRequest,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: SocialController = Depends(_ctrl),
):
    """Inicia flujo OAuth para conectar cuenta de Instagram o Facebook vía Zernio."""
    return ctrl.iniciar_oauth(body, x_marca_id, current_user)


@router.post("/conectar/callback")
def completar_oauth(
    body: CompletarOAuthRequest,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: SocialController = Depends(_ctrl),
):
    """Completa flujo OAuth con el code recibido de Zernio."""
    return ctrl.completar_oauth(body, x_marca_id, current_user)


# --- Publicación ---

@router.post("/publicar")
def publicar(
    body: PublicarRequest,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: SocialController = Depends(_ctrl),
):
    """Publica un post de forma inmediata vía Zernio."""
    return ctrl.publicar(body, x_marca_id, current_user)


@router.post("/programar")
def programar(
    body: ProgramarRequest,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: SocialController = Depends(_ctrl),
):
    """Programa un post para fecha/hora futura vía Zernio."""
    return ctrl.programar(body, x_marca_id, current_user)


# --- Cuentas (manual + legacy) ---

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
    """Conecta o actualiza una cuenta social manualmente."""
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


# --- Publicaciones ---

@router.get("/publicaciones")
def listar_publicaciones(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: SocialController = Depends(_ctrl),
):
    """Lista el historial de publicaciones realizadas por la marca."""
    return ctrl.listar_publicaciones(x_marca_id, current_user)


@router.patch("/publicaciones/{publicacion_id}/cancelar")
def cancelar_publicacion(
    publicacion_id: UUID,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cancela una publicación programada."""
    from repositories import publicaciones_repository as pub_repo
    result = pub_repo.actualizar_estado(db, publicacion_id, "cancelado")
    if not result:
        from middleware.error_handler import AppError
        raise AppError("Publicación no encontrada", "NOT_FOUND", 404)
    db.commit()
    return result


@router.post("/publicaciones/{publicacion_id}/monitorear")
def monitorear(
    publicacion_id: UUID,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: SocialController = Depends(_ctrl),
):
    """Obtiene métricas de las 2hs post-publicación y detecta engagement bajo."""
    return ctrl.monitorear(publicacion_id, x_marca_id, current_user)


# --- Webhook ---

@router.post("/webhook/zernio")
async def webhook_zernio(
    request: Request,
    ctrl: SocialController = Depends(_ctrl),
):
    """Webhook de confirmación de publicación de Zernio (placeholder)."""
    payload = await request.json()
    return ctrl.webhook(payload)
