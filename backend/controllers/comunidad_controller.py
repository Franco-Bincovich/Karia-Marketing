"""Adaptador HTTP para el módulo de Comunidad y Social Listening."""

from __future__ import annotations

import logging
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from middleware.error_handler import AppError
from services import comunidad_service, social_listening_service

logger = logging.getLogger(__name__)


class MensajeRequest(BaseModel):
    red_social: str
    tipo: str = Field(pattern="^(comentario|dm|mencion|story_reply)$")
    autor_username: Optional[str] = None
    autor_id_externo: Optional[str] = None
    contenido: str = Field(min_length=1)
    clasificacion: str = "consulta_comercial"
    sentimiento: str = "neutro"


class ResponderRequest(BaseModel):
    respuesta: str = Field(min_length=1)


class ConfigComunidadRequest(BaseModel):
    criterios_escalado: Optional[list] = None
    tiempo_respuesta_max: Optional[int] = None
    responder_agresivos: Optional[bool] = None
    responder_spam: Optional[bool] = None
    modo: Optional[str] = Field(default=None, pattern="^(autopilot|copilot)$")


class ConfigListeningRequest(BaseModel):
    terminos_marca: Optional[list] = None
    terminos_competidores: Optional[list] = None
    keywords_sector: Optional[list] = None
    notificar_negativas: Optional[bool] = None
    notificar_competidores: Optional[bool] = None
    umbral_urgencia: Optional[int] = None


def _marca(x_marca_id: Optional[str]) -> UUID:
    """Extrae y valida marca_id del header."""
    if not x_marca_id:
        raise AppError("Header X-Marca-ID es requerido", "MISSING_MARCA_ID", 400)
    try:
        return UUID(x_marca_id)
    except ValueError:
        raise AppError("X-Marca-ID debe ser un UUID válido", "INVALID_MARCA_ID", 400)


class ComunidadController:
    def __init__(self, db: Session):
        self.db = db

    def listar_mensajes(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Lista mensajes de comunidad."""
        from repositories import mensajes_comunidad_repository

        items = mensajes_comunidad_repository.listar(self.db, _marca(x_marca_id))
        return {"data": items, "count": len(items)}

    def mensajes_pendientes(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Lista mensajes pendientes de respuesta."""
        items = comunidad_service.listar_pendientes(self.db, _marca(x_marca_id))
        return {"data": items, "count": len(items)}

    def recibir_mensaje(self, body: MensajeRequest, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Procesa un mensaje entrante."""
        return comunidad_service.procesar_mensaje(self.db, _marca(x_marca_id), body.model_dump())

    def responder_mensaje(self, msg_id: UUID, body: ResponderRequest, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Responde un mensaje manualmente."""
        from repositories import mensajes_comunidad_repository

        r = mensajes_comunidad_repository.marcar_respondido(self.db, msg_id, body.respuesta)
        if not r:
            raise AppError("Mensaje no encontrado", "NOT_FOUND", 404)
        self.db.commit()
        return r

    def historial(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Historial de mensajes gestionados."""
        items = comunidad_service.listar_historial(self.db, _marca(x_marca_id))
        return {"data": items, "count": len(items)}

    def leads(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Lista leads detectados en DMs."""
        items = comunidad_service.listar_leads_detectados(self.db, _marca(x_marca_id))
        return {"data": items, "count": len(items)}

    def menciones(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Lista menciones."""
        from repositories import menciones_repository

        items = menciones_repository.listar(self.db, _marca(x_marca_id))
        return {"data": items, "count": len(items)}

    def menciones_urgentes(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Lista menciones urgentes."""
        from repositories import menciones_repository

        items = menciones_repository.listar_urgentes(self.db, _marca(x_marca_id))
        return {"data": items, "count": len(items)}

    def monitorear(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Ejecuta monitoreo de social listening."""
        return social_listening_service.ejecutar_monitoreo(self.db, _marca(x_marca_id))

    def sentimiento(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Análisis de sentimiento de la marca."""
        return social_listening_service.analizar_sentimiento_marca(self.db, _marca(x_marca_id))

    def config_comunidad(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Obtiene configuración de comunidad."""
        from repositories import config_comunidad_repository

        return config_comunidad_repository.obtener_o_crear(self.db, _marca(x_marca_id))

    def actualizar_config_comunidad(self, body: ConfigComunidadRequest, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Actualiza configuración de comunidad."""
        from repositories import config_comunidad_repository

        data = {k: v for k, v in body.model_dump().items() if v is not None}
        return config_comunidad_repository.actualizar(self.db, _marca(x_marca_id), data)

    def config_listening(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Obtiene configuración de listening."""
        from repositories import config_listening_repository

        return config_listening_repository.obtener_o_crear(self.db, _marca(x_marca_id))

    def actualizar_config_listening(self, body: ConfigListeningRequest, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Actualiza configuración de listening."""
        from repositories import config_listening_repository

        data = {k: v for k, v in body.model_dump().items() if v is not None}
        return config_listening_repository.actualizar(self.db, _marca(x_marca_id), data)
