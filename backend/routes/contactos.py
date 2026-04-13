"""Rutas de prospección de contactos — Módulo 2."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from controllers.contactos_controller import (
    BuscarIARequest,
    ContactoManualRequest,
    ContactosController,
    GuardarSeleccionRequest,
)
from integrations.database import get_db
from middleware.auth import get_current_user

router = APIRouter(prefix="/api/contactos", tags=["contactos"])


def _ctrl(db: Session = Depends(get_db)) -> ContactosController:
    return ContactosController(db)


@router.get("")
def listar_contactos(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: ContactosController = Depends(_ctrl),
):
    """Lista los contactos de la marca activa (header X-Marca-ID)."""
    return ctrl.listar(x_marca_id, current_user)


@router.post("/buscar-ia")
def buscar_con_ia(
    body: BuscarIARequest,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: ContactosController = Depends(_ctrl),
):
    """Busca prospectos con Claude + web search. No persiste — devuelve candidatos."""
    return ctrl.buscar_ia(body, x_marca_id, current_user)


@router.post("/guardar")
def guardar_seleccion(
    body: GuardarSeleccionRequest,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: ContactosController = Depends(_ctrl),
):
    """Guarda la selección de contactos encontrados por IA. Omite duplicados."""
    return ctrl.guardar_seleccion(body, x_marca_id, current_user)


@router.post("/manual")
def agregar_manual(
    body: ContactoManualRequest,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: ContactosController = Depends(_ctrl),
):
    """Agrega un contacto cargado manualmente por el usuario."""
    return ctrl.agregar_manual(body, x_marca_id, current_user)


@router.delete("/{contacto_id}")
def eliminar_contacto(
    contacto_id: UUID,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: ContactosController = Depends(_ctrl),
):
    """Elimina un contacto verificando que pertenezca a la marca."""
    return ctrl.eliminar(contacto_id, x_marca_id, current_user)
