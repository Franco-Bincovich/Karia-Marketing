"""Adaptador HTTP para el módulo de Onboarding y Memoria de Marca."""
from __future__ import annotations

import logging
from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.orm import Session

from middleware.error_handler import AppError
from services import memoria_service, onboarding_service

logger = logging.getLogger(__name__)


class PasoRequest(BaseModel):
    datos: dict


class GuardarRespuestasRequest(BaseModel):
    respuestas: dict


class SugerirRequest(BaseModel):
    pregunta_id: int


class AutocompletarRequest(BaseModel):
    nombre_marca: str


class MemoriaUpdateRequest(BaseModel):
    datos: dict


def _marca(x_marca_id: Optional[str]) -> UUID:
    """Extrae y valida marca_id del header."""
    if not x_marca_id:
        raise AppError("Header X-Marca-ID es requerido", "MISSING_MARCA_ID", 400)
    try:
        return UUID(x_marca_id)
    except ValueError:
        raise AppError("X-Marca-ID debe ser un UUID válido", "INVALID_MARCA_ID", 400)


class OnboardingController:
    def __init__(self, db: Session):
        self.db = db

    def estado(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Obtiene estado del onboarding con preguntas según plan."""
        return onboarding_service.obtener_estado(
            self.db, _marca(x_marca_id), rol=current_user.get("rol", ""),
        )

    def iniciar(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Inicia el onboarding de una marca."""
        return onboarding_service.iniciar_onboarding(self.db, _marca(x_marca_id))

    def guardar(self, body: GuardarRespuestasRequest,
                x_marca_id: Optional[str], current_user: dict) -> dict:
        """Guarda progreso parcial del cuestionario."""
        return onboarding_service.guardar_respuestas(
            self.db, _marca(x_marca_id), body.respuestas, UUID(current_user["sub"]),
        )

    def completar(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Marca onboarding como completo y genera perfil de marca."""
        return onboarding_service.completar_onboarding(
            self.db, _marca(x_marca_id), UUID(current_user["sub"]),
        )

    def perfil(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Retorna el perfil de marca consolidado."""
        return onboarding_service.obtener_perfil(self.db, _marca(x_marca_id))

    def sugerir(self, body: SugerirRequest,
                x_marca_id: Optional[str], current_user: dict) -> dict:
        """Sugiere respuesta via IA. Premium o superadmin."""
        return onboarding_service.sugerir_respuesta(
            self.db, _marca(x_marca_id), body.pregunta_id,
            rol=current_user.get("rol", ""),
        )

    def autocompletar(self, body: AutocompletarRequest,
                      x_marca_id: Optional[str], current_user: dict) -> dict:
        """Autocompleta perfil buscando info pública de la marca. Premium o superadmin."""
        return onboarding_service.autocompletar_perfil(
            self.db, _marca(x_marca_id), body.nombre_marca,
            rol=current_user.get("rol", ""),
        )

    # --- Legacy ---

    def completar_paso(self, numero: int, body: PasoRequest,
                       x_marca_id: Optional[str], current_user: dict) -> dict:
        """Completa un paso del onboarding legacy (10 pasos)."""
        return onboarding_service.completar_paso(
            self.db, _marca(x_marca_id), numero,
            body.datos, UUID(current_user["sub"]),
        )

    def obtener_memoria(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Obtiene la memoria de marca completa."""
        from repositories import memoria_marca_repository
        return memoria_marca_repository.obtener_o_crear(self.db, _marca(x_marca_id))

    def actualizar_memoria(self, body: MemoriaUpdateRequest,
                           x_marca_id: Optional[str], current_user: dict) -> dict:
        """Actualiza la memoria de marca manualmente."""
        from repositories import memoria_marca_repository
        return memoria_marca_repository.actualizar(self.db, _marca(x_marca_id), body.datos)

    def memoria_agente(self, agente: str, x_marca_id: Optional[str],
                       current_user: dict) -> dict:
        """Retorna memoria formateada para un agente específico."""
        texto = memoria_service.obtener_para_agente(self.db, _marca(x_marca_id), agente)
        return {"agente": agente, "memoria": texto}

    def regenerar_memoria(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Regenera la memoria de marca para los agentes."""
        texto = onboarding_service.regenerar_memoria(self.db, _marca(x_marca_id))
        return {"memoria": texto}
