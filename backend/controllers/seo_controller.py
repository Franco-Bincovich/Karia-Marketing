"""Adaptador HTTP para el módulo de SEO."""

from __future__ import annotations

import logging
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from middleware.error_handler import AppError
from services import auditoria_seo_service, briefs_seo_service, keywords_service

logger = logging.getLogger(__name__)


class InvestigarRequest(BaseModel):
    query: str = Field(min_length=2)


class AuditarRequest(BaseModel):
    url: str = Field(min_length=5)


class BriefRequest(BaseModel):
    keyword_principal: str = Field(min_length=2)
    keywords_secundarias: Optional[str] = None


class CompetidorRequest(BaseModel):
    dominio: str = Field(min_length=3)


class ConfigSeoRequest(BaseModel):
    sitio_web: Optional[str] = None
    frecuencia_reporte: Optional[str] = Field(default=None, pattern="^(semanal|quincenal|mensual)$")
    semrush_proyecto_id: Optional[str] = None
    search_console_conectado: Optional[bool] = None
    competidores: Optional[str] = None


def _marca(x_marca_id: Optional[str]) -> UUID:
    """Extrae y valida marca_id del header."""
    if not x_marca_id:
        raise AppError("Header X-Marca-ID es requerido", "MISSING_MARCA_ID", 400)
    try:
        return UUID(x_marca_id)
    except ValueError:
        raise AppError("X-Marca-ID debe ser un UUID válido", "INVALID_MARCA_ID", 400)


class SeoController:
    def __init__(self, db: Session):
        self.db = db

    def listar_keywords(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Lista keywords monitoreadas de la marca."""
        from repositories import keywords_repository

        items = keywords_repository.listar(self.db, _marca(x_marca_id))
        return {"data": items, "count": len(items)}

    def investigar_keywords(self, body: InvestigarRequest, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Busca nuevas keywords via Semrush."""
        items = keywords_service.investigar_keywords(self.db, _marca(x_marca_id), body.query)
        return {"data": items, "count": len(items)}

    def monitorear_posiciones(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Actualiza posiciones y detecta caídas."""
        alertas = keywords_service.monitorear_posiciones(self.db, _marca(x_marca_id))
        return {"alertas": alertas, "count": len(alertas)}

    def listar_auditoria(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Lista hallazgos de auditoría SEO."""
        items = auditoria_seo_service.listar(self.db, _marca(x_marca_id))
        return {"data": items, "count": len(items)}

    def auditar_sitio(self, body: AuditarRequest, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Audita una URL y genera recomendaciones."""
        items = auditoria_seo_service.auditar_sitio(self.db, _marca(x_marca_id), body.url)
        return {"data": items, "count": len(items)}

    def marcar_implementado(self, item_id: UUID, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Marca hallazgo como implementado."""
        return auditoria_seo_service.marcar_implementado(self.db, item_id, _marca(x_marca_id))

    def listar_briefs(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Lista briefs SEO generados."""
        items = briefs_seo_service.listar(self.db, _marca(x_marca_id))
        return {"data": items, "count": len(items)}

    def generar_brief(self, body: BriefRequest, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Genera un nuevo brief SEO con Claude."""
        return briefs_seo_service.generar_brief(
            self.db,
            _marca(x_marca_id),
            body.keyword_principal,
            body.keywords_secundarias or "",
        )

    def obtener_config(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Obtiene configuración SEO de la marca."""
        from repositories import config_seo_repository

        return config_seo_repository.obtener_o_crear(self.db, _marca(x_marca_id))

    def actualizar_config(self, body: ConfigSeoRequest, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Actualiza configuración SEO."""
        from repositories import config_seo_repository

        data = {k: v for k, v in body.model_dump().items() if v is not None}
        return config_seo_repository.actualizar(self.db, _marca(x_marca_id), data)

    def analizar_competidor(self, body: CompetidorRequest, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Analiza keywords de un competidor."""
        return keywords_service.analizar_competidor(self.db, _marca(x_marca_id), body.dominio)
