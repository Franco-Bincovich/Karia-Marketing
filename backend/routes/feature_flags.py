"""Rutas de gestión de feature flags."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from controllers.clientes_controller import ClientesController, FeatureFlagRequest
from integrations.database import get_db
from middleware.auth import get_current_user, require_admin_or_above

router = APIRouter(prefix="/api/feature-flags", tags=["feature-flags"])


@router.get("")
def listar_feature_flags(
    cliente_id: UUID = Query(...),
    marca_id: Optional[UUID] = Query(default=None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista los feature flags de un cliente, opcionalmente filtrado por marca."""
    return ClientesController(db).listar_feature_flags(cliente_id, marca_id)


@router.patch("/{feature}")
def actualizar_feature_flag(
    feature: str,
    body: FeatureFlagRequest,
    cliente_id: UUID = Query(...),
    current_user: dict = Depends(require_admin_or_above()),
    db: Session = Depends(get_db),
):
    """Actualiza o crea un feature flag para un cliente."""
    return ClientesController(db).actualizar_feature_flag(cliente_id, feature, body)
