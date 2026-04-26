"""Rutas del módulo Onboarding, Memoria de Marca y Perfil."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, Header, UploadFile
from sqlalchemy.orm import Session

from controllers.onboarding_controller import (
    AutocompletarRequest,
    GuardarRespuestasRequest,
    MemoriaUpdateRequest,
    OnboardingController,
    PasoRequest,
    SugerirRequest,
)
from integrations.database import get_db
from middleware.auth import get_current_user

router = APIRouter(tags=["onboarding"])


def _ctrl(db: Session = Depends(get_db)) -> OnboardingController:
    return OnboardingController(db)


# --- Onboarding cuestionario ---


@router.get("/api/onboarding/estado")
def estado(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: OnboardingController = Depends(_ctrl),
):
    """Estado del onboarding con preguntas según plan."""
    return ctrl.estado(x_marca_id, current_user)


@router.post("/api/onboarding/iniciar")
def iniciar(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: OnboardingController = Depends(_ctrl),
):
    """Inicia el proceso de onboarding para una marca."""
    return ctrl.iniciar(x_marca_id, current_user)


@router.post("/api/onboarding/guardar")
def guardar(
    body: GuardarRespuestasRequest,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: OnboardingController = Depends(_ctrl),
):
    """Guarda progreso parcial del cuestionario."""
    return ctrl.guardar(body, x_marca_id, current_user)


@router.post("/api/onboarding/completar")
def completar(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: OnboardingController = Depends(_ctrl),
):
    """Marca el onboarding como completo y genera perfil de marca consolidado."""
    return ctrl.completar(x_marca_id, current_user)


# --- IA Premium ---


@router.post("/api/onboarding/sugerir")
def sugerir(
    body: SugerirRequest,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: OnboardingController = Depends(_ctrl),
):
    """Sugiere respuesta via IA para una pregunta del onboarding. Solo Premium."""
    return ctrl.sugerir(body, x_marca_id, current_user)


@router.post("/api/onboarding/autocompletar")
def autocompletar(
    body: AutocompletarRequest,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: OnboardingController = Depends(_ctrl),
):
    """Autocompleta perfil buscando info pública de la marca. Solo Premium."""
    return ctrl.autocompletar(body, x_marca_id, current_user)


# --- Perfil de marca ---


@router.get("/api/marca/perfil")
def perfil_marca(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: OnboardingController = Depends(_ctrl),
):
    """Perfil de marca consolidado — usado por los agentes de IA."""
    return ctrl.perfil(x_marca_id, current_user)


# --- Documentos de marca ---


@router.post("/api/marca/documentos/subir")
async def subir_documento(
    file: UploadFile = File(...),
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Sube un documento (PDF, DOCX, TXT) para contexto de marca."""
    from controllers.onboarding_controller import _marca
    from services import documentos_service

    content = await file.read()
    return documentos_service.subir(db, _marca(x_marca_id), file.filename, content)


@router.get("/api/marca/documentos")
def listar_documentos(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista documentos subidos de la marca."""
    from controllers.onboarding_controller import _marca
    from services import documentos_service

    items = documentos_service.listar(db, _marca(x_marca_id))
    return {"data": items, "count": len(items)}


@router.delete("/api/marca/documentos/{doc_id}")
def eliminar_documento(
    doc_id: UUID,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Elimina un documento de la marca."""
    from controllers.onboarding_controller import _marca
    from services import documentos_service

    documentos_service.eliminar(db, doc_id, _marca(x_marca_id))
    return {"message": "Documento eliminado"}


# --- Legacy: pasos individuales ---


@router.post("/api/onboarding/paso/{numero}")
def completar_paso(
    numero: int,
    body: PasoRequest,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: OnboardingController = Depends(_ctrl),
):
    """Completa un paso del onboarding legacy (1-10)."""
    return ctrl.completar_paso(numero, body, x_marca_id, current_user)


# --- Memoria de marca ---


@router.get("/api/onboarding/memoria")
def obtener_memoria(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: OnboardingController = Depends(_ctrl),
):
    """Obtiene la memoria de marca completa."""
    return ctrl.obtener_memoria(x_marca_id, current_user)


@router.patch("/api/onboarding/memoria")
def actualizar_memoria(
    body: MemoriaUpdateRequest,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: OnboardingController = Depends(_ctrl),
):
    """Actualiza la memoria de marca manualmente."""
    return ctrl.actualizar_memoria(body, x_marca_id, current_user)


@router.get("/api/onboarding/memoria/agente/{agente}")
def memoria_agente(
    agente: str,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: OnboardingController = Depends(_ctrl),
):
    """Retorna memoria formateada para un agente específico."""
    return ctrl.memoria_agente(agente, x_marca_id, current_user)


@router.post("/api/onboarding/memoria/regenerar")
def regenerar_memoria(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: OnboardingController = Depends(_ctrl),
):
    """Regenera la memoria de marca para inyectar en agentes."""
    return ctrl.regenerar_memoria(x_marca_id, current_user)
