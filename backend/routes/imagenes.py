"""Rutas del módulo de Imágenes IA — Módulo 6."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from controllers.imagen_controller import (
    GenerarImagenRequest, GenerarParaContenidoRequest,
    GuardarOpenAIKeyRequest, ImagenController,
)
from integrations.database import get_db
from middleware.auth import get_current_user

router = APIRouter(prefix="/api/imagenes", tags=["imagenes"])


def _ctrl(db: Session = Depends(get_db)) -> ImagenController:
    return ImagenController(db)


@router.post("/generar")
def generar(
    body: GenerarImagenRequest,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: ImagenController = Depends(_ctrl),
):
    """Genera imagen desde descripción libre con perfil de marca opcional."""
    return ctrl.generar(body, x_marca_id, current_user)


@router.post("/generar-para-contenido/{contenido_id}")
def generar_para_contenido(
    contenido_id: UUID,
    body: GenerarParaContenidoRequest,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: ImagenController = Depends(_ctrl),
):
    """Genera imagen para un contenido existente usando el copy como contexto."""
    return ctrl.generar_para_contenido(contenido_id, body, x_marca_id, current_user)


@router.get("")
def listar(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: ImagenController = Depends(_ctrl),
):
    """Lista imágenes generadas del cliente."""
    return ctrl.listar(x_marca_id, current_user)


@router.post("/{imagen_id}/asociar-contenido/{contenido_id}")
def asociar(
    imagen_id: UUID,
    contenido_id: UUID,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: ImagenController = Depends(_ctrl),
):
    """Asocia una imagen existente a un contenido."""
    return ctrl.asociar(imagen_id, contenido_id, x_marca_id, current_user)


@router.post("/openai-key")
def guardar_key(
    body: GuardarOpenAIKeyRequest,
    current_user: dict = Depends(get_current_user),
    ctrl: ImagenController = Depends(_ctrl),
):
    """Guarda API key propia de OpenAI. Solo Premium y superadmin."""
    return ctrl.guardar_key(body, current_user)
