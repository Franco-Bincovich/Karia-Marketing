"""Rutas del módulo de Imágenes IA — Módulo 6."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header, UploadFile, File
from sqlalchemy.orm import Session

from controllers.imagen_controller import (
    GenerarCarruselRequest, GenerarImagenRequest, GenerarParaContenidoRequest,
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


@router.post("/generar-carrusel/{contenido_id}")
def generar_carrusel(
    contenido_id: UUID,
    body: GenerarCarruselRequest,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: ImagenController = Depends(_ctrl),
):
    """Genera N slides de carrusel con copies + imágenes."""
    return ctrl.generar_carrusel(contenido_id, body, x_marca_id, current_user)


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


# --- Biblioteca (upload manual) ---

@router.post("/biblioteca/subir")
async def biblioteca_subir(
    file: UploadFile = File(...),
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Sube imagen manualmente a la biblioteca."""
    from services import imagen_service
    from controllers.imagen_controller import _marca
    content = await file.read()
    return imagen_service.biblioteca_subir(db, _marca(x_marca_id), file.filename, content)


@router.get("/biblioteca")
def biblioteca_listar(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista imágenes subidas manualmente."""
    from services import imagen_service
    from controllers.imagen_controller import _marca
    items = imagen_service.biblioteca_listar(db, _marca(x_marca_id))
    return {"data": items, "count": len(items)}


@router.delete("/biblioteca/{imagen_id}")
def biblioteca_eliminar(
    imagen_id: UUID,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Elimina imagen de la biblioteca."""
    from services import imagen_service
    from controllers.imagen_controller import _marca
    imagen_service.biblioteca_eliminar(db, _marca(x_marca_id), imagen_id)
    return {"message": "Imagen eliminada"}
