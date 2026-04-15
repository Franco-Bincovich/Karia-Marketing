"""Rutas del módulo de Contenido IA — Módulo 5."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.orm import Session

from controllers.contenido_controller import (
    AprobarRequest, ContenidoController, EditarRequest,
    GenerarRequest, GuardarApiKeyRequest, PublicarDirectoRequest,
    RechazarRequest, TemplateRequest,
)
from integrations.database import get_db
from middleware.auth import get_current_user

router = APIRouter(prefix="/api/contenido", tags=["contenido"])


def _ctrl(db: Session = Depends(get_db)) -> ContenidoController:
    return ContenidoController(db)


@router.post("/generar")
def generar(
    body: GenerarRequest,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: ContenidoController = Depends(_ctrl),
):
    """Genera 3 variantes A/B/C con perfil de marca como contexto."""
    return ctrl.generar(body, x_marca_id, current_user)


@router.get("")
def listar(
    x_marca_id: Optional[str] = Header(default=None),
    estado: Optional[str] = Query(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: ContenidoController = Depends(_ctrl),
):
    """Lista contenido con filtro opcional de estado."""
    return ctrl.listar(x_marca_id, current_user, estado=estado)


@router.get("/usage")
def usage(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: ContenidoController = Depends(_ctrl),
):
    """Info de uso del mes: posts, límite, plan, autopilot."""
    return ctrl.usage(x_marca_id, current_user)


@router.post("/api-key")
def guardar_api_key(
    body: GuardarApiKeyRequest,
    current_user: dict = Depends(get_current_user),
    ctrl: ContenidoController = Depends(_ctrl),
):
    """Guarda API key propia de Anthropic. Solo Premium."""
    return ctrl.guardar_api_key(body, current_user)


@router.get("/templates")
def listar_templates(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: ContenidoController = Depends(_ctrl),
):
    return ctrl.listar_templates(x_marca_id, current_user)


@router.post("/templates")
def crear_template(
    body: TemplateRequest,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: ContenidoController = Depends(_ctrl),
):
    return ctrl.crear_template(body, x_marca_id, current_user)


@router.delete("/templates/{template_id}")
def eliminar_template(
    template_id: UUID,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: ContenidoController = Depends(_ctrl),
):
    return ctrl.eliminar_template(template_id, x_marca_id, current_user)


@router.get("/{contenido_id}/versiones")
def versiones(
    contenido_id: UUID,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: ContenidoController = Depends(_ctrl),
):
    return ctrl.versiones(contenido_id, x_marca_id, current_user)


@router.post("/{contenido_id}/aprobar")
def aprobar(
    contenido_id: UUID,
    body: AprobarRequest,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: ContenidoController = Depends(_ctrl),
):
    """Aprueba una variante (Copilot)."""
    return ctrl.aprobar(contenido_id, body, x_marca_id, current_user)


@router.post("/{contenido_id}/publicar-directo")
def publicar_directo(
    contenido_id: UUID,
    body: PublicarDirectoRequest,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: ContenidoController = Depends(_ctrl),
):
    """Aprueba y publica inmediatamente vía Zernio. Solo Premium y superadmin."""
    return ctrl.publicar_directo(contenido_id, body, x_marca_id, current_user)


@router.post("/{contenido_id}/rechazar")
def rechazar(
    contenido_id: UUID,
    body: RechazarRequest,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: ContenidoController = Depends(_ctrl),
):
    return ctrl.rechazar(contenido_id, body, x_marca_id, current_user)


@router.post("/{contenido_id}/editar")
def editar(
    contenido_id: UUID,
    body: EditarRequest,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: ContenidoController = Depends(_ctrl),
):
    return ctrl.editar(contenido_id, body, x_marca_id, current_user)
