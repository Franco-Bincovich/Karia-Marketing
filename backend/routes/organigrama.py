"""Ruta del organigrama de la agencia."""

from typing import Optional

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from integrations.database import get_db
from middleware.auth import get_current_user
from middleware.error_handler import AppError
from services import organigrama_service as svc

router = APIRouter(prefix="/api/organigrama", tags=["organigrama"])


def _marca(x_marca_id: Optional[str]):
    from uuid import UUID
    if not x_marca_id:
        raise AppError("Header X-Marca-ID requerido", "MISSING_MARCA_ID", 400)
    return UUID(x_marca_id)


@router.get("")
def obtener_organigrama(
    x_marca_id: Optional[str] = Header(default=None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Estructura jerárquica completa de la agencia con estado real."""
    marca_id = _marca(x_marca_id)
    rol = current_user.get("rol", "")
    return svc.obtener_organigrama(db, marca_id, rol=rol)
