"""Rutas del módulo SEO — keywords, auditoría, briefs y configuración."""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from controllers.seo_controller import (
    AuditarRequest, BriefRequest, CompetidorRequest,
    ConfigSeoRequest, InvestigarRequest, SeoController,
)
from integrations.database import get_db
from middleware.auth import get_current_user

router = APIRouter(prefix="/api/seo", tags=["seo"])


def _ctrl(db: Session = Depends(get_db)) -> SeoController:
    return SeoController(db)


@router.get("/keywords")
def listar_keywords(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: SeoController = Depends(_ctrl),
):
    """Lista keywords monitoreadas de la marca."""
    return ctrl.listar_keywords(x_marca_id, current_user)


@router.post("/keywords/investigar")
def investigar_keywords(
    body: InvestigarRequest,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: SeoController = Depends(_ctrl),
):
    """Busca nuevas keywords via Semrush y las guarda."""
    return ctrl.investigar_keywords(body, x_marca_id, current_user)


@router.post("/keywords/monitorear")
def monitorear_posiciones(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: SeoController = Depends(_ctrl),
):
    """Actualiza posiciones de keywords y detecta caídas."""
    return ctrl.monitorear_posiciones(x_marca_id, current_user)


@router.get("/auditoria")
def listar_auditoria(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: SeoController = Depends(_ctrl),
):
    """Lista hallazgos de auditoría técnica SEO."""
    return ctrl.listar_auditoria(x_marca_id, current_user)


@router.post("/auditoria")
def auditar_sitio(
    body: AuditarRequest,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: SeoController = Depends(_ctrl),
):
    """Audita una URL y genera recomendaciones técnicas."""
    return ctrl.auditar_sitio(body, x_marca_id, current_user)


@router.patch("/auditoria/{item_id}/implementado")
def marcar_implementado(
    item_id: UUID,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: SeoController = Depends(_ctrl),
):
    """Marca un hallazgo de auditoría como implementado."""
    return ctrl.marcar_implementado(item_id, x_marca_id, current_user)


@router.get("/briefs")
def listar_briefs(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: SeoController = Depends(_ctrl),
):
    """Lista briefs SEO generados."""
    return ctrl.listar_briefs(x_marca_id, current_user)


@router.post("/briefs")
def generar_brief(
    body: BriefRequest,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: SeoController = Depends(_ctrl),
):
    """Genera un nuevo brief SEO con IA."""
    return ctrl.generar_brief(body, x_marca_id, current_user)


@router.get("/config")
def obtener_config(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: SeoController = Depends(_ctrl),
):
    """Obtiene configuración SEO de la marca."""
    return ctrl.obtener_config(x_marca_id, current_user)


@router.patch("/config")
def actualizar_config(
    body: ConfigSeoRequest,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: SeoController = Depends(_ctrl),
):
    """Actualiza la configuración SEO de la marca."""
    return ctrl.actualizar_config(body, x_marca_id, current_user)


@router.post("/competidor")
def analizar_competidor(
    body: CompetidorRequest,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    ctrl: SeoController = Depends(_ctrl),
):
    """Analiza keywords de un competidor."""
    return ctrl.analizar_competidor(body, x_marca_id, current_user)
