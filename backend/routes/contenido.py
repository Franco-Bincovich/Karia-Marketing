"""Rutas del módulo de Contenido IA — Módulo 3."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from controllers.contenido_controller import (
    AprobarRequest, ContenidoController, EditarRequest,
    GenerarRequest, RechazarRequest, TemplateRequest,
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
    """Genera variantes A/B con Claude. Siempre retorna dos versiones."""
    return ctrl.generar(body, x_marca_id, current_user)


@router.get("")
def listar(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: ContenidoController = Depends(_ctrl),
):
    """Lista todo el contenido de la marca activa."""
    return ctrl.listar(x_marca_id, current_user)


@router.get("/templates")
def listar_templates(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: ContenidoController = Depends(_ctrl),
):
    """Lista los templates reutilizables de la marca."""
    return ctrl.listar_templates(x_marca_id, current_user)


@router.post("/templates")
def crear_template(
    body: TemplateRequest,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: ContenidoController = Depends(_ctrl),
):
    """Crea un template reutilizable para la marca."""
    return ctrl.crear_template(body, x_marca_id, current_user)


@router.delete("/templates/{template_id}")
def eliminar_template(
    template_id: UUID,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: ContenidoController = Depends(_ctrl),
):
    """Elimina un template de la marca."""
    return ctrl.eliminar_template(template_id, x_marca_id, current_user)


@router.get("/{contenido_id}/versiones")
def versiones(
    contenido_id: UUID,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: ContenidoController = Depends(_ctrl),
):
    """Retorna el historial de versiones de una pieza de contenido."""
    return ctrl.versiones(contenido_id, x_marca_id, current_user)


@router.post("/{contenido_id}/aprobar")
def aprobar(
    contenido_id: UUID,
    body: AprobarRequest,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: ContenidoController = Depends(_ctrl),
):
    """Aprueba una pieza con la variante seleccionada. Registra aprendizaje."""
    return ctrl.aprobar(contenido_id, body, x_marca_id, current_user)


@router.post("/{contenido_id}/rechazar")
def rechazar(
    contenido_id: UUID,
    body: RechazarRequest,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: ContenidoController = Depends(_ctrl),
):
    """Rechaza con comentario y regenera nuevas variantes A/B incorporando el feedback."""
    return ctrl.rechazar(contenido_id, body, x_marca_id, current_user)


@router.post("/{contenido_id}/editar")
def editar(
    contenido_id: UUID,
    body: EditarRequest,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: ContenidoController = Depends(_ctrl),
):
    """Guarda edición manual del cliente. Registra para autoaprendizaje."""
    return ctrl.editar(contenido_id, body, x_marca_id, current_user)
