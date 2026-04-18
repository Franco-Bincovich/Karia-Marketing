"""Rutas de configuración de API keys — solo superadmin."""

from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from integrations.database import get_db
from middleware.auth import require_superadmin
from services import api_keys_service as svc

router = APIRouter(prefix="/api/config/api-keys", tags=["config"])


class GuardarKeyRequest(BaseModel):
    api_key: str


@router.get("")
def listar(
    current_user: dict = Depends(require_superadmin()),
    db: Session = Depends(get_db),
):
    """Lista servicios con estado de configuración. Solo superadmin."""
    cliente_id = UUID(current_user["cliente_id"])
    return {"data": svc.listar(db, cliente_id)}


@router.post("/{servicio}")
def guardar(
    servicio: str,
    body: GuardarKeyRequest,
    current_user: dict = Depends(require_superadmin()),
    db: Session = Depends(get_db),
):
    """Guarda o actualiza API key encriptada. Solo superadmin."""
    cliente_id = UUID(current_user["cliente_id"])
    return svc.guardar(db, cliente_id, servicio, body.api_key)


@router.delete("/{servicio}")
def eliminar(
    servicio: str,
    current_user: dict = Depends(require_superadmin()),
    db: Session = Depends(get_db),
):
    """Elimina API key. Solo superadmin."""
    cliente_id = UUID(current_user["cliente_id"])
    return svc.eliminar(db, cliente_id, servicio)
