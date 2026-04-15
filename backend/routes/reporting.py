"""Rutas dedicadas de Reporting — M10."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from integrations.database import get_db
from middleware.auth import get_current_user
from middleware.error_handler import AppError
from services import reporting_service

router = APIRouter(prefix="/api/reporting", tags=["reporting"])


class GenerarReporteRequest(BaseModel):
    periodo: str = Field(default="semanal", pattern="^(diario|semanal|mensual)$")


def _marca(x_marca_id: Optional[str]) -> UUID:
    if not x_marca_id:
        raise AppError("Header X-Marca-ID es requerido", "MISSING_MARCA_ID", 400)
    try:
        return UUID(x_marca_id)
    except ValueError:
        raise AppError("X-Marca-ID debe ser un UUID válido", "INVALID_MARCA_ID", 400)


@router.post("/generar")
def generar(
    body: GenerarReporteRequest,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Genera nuevo reporte del período con resumen ejecutivo IA."""
    return reporting_service.generar_reporte(db, _marca(x_marca_id), body.periodo)


@router.get("")
def listar(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista reportes anteriores."""
    from repositories import reportes_repository
    items = reportes_repository.listar(db, _marca(x_marca_id))
    return {"data": items, "count": len(items)}


@router.get("/{reporte_id}")
def obtener(
    reporte_id: UUID,
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Reporte específico completo."""
    from repositories import reportes_repository
    reportes = reportes_repository.listar(db, _marca(x_marca_id))
    reporte = next((r for r in reportes if r["id"] == str(reporte_id)), None)
    if not reporte:
        raise AppError("Reporte no encontrado", "NOT_FOUND", 404)
    return reporte
