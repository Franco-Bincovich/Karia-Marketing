"""Rutas de gestión de clientes y marcas."""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from controllers.clientes_controller import (
    CambiarEstadoRequest,
    ClientesController,
    CrearClienteRequest,
    CrearMarcaRequest,
)
from integrations.database import get_db
from middleware.auth import get_current_user, require_admin_or_above, require_superadmin

router = APIRouter(prefix="/api/clientes", tags=["clientes"])


@router.post("")
def crear_cliente(
    body: CrearClienteRequest,
    current_user: dict = Depends(require_superadmin()),
    db: Session = Depends(get_db),
):
    """Crea un nuevo cliente. Solo superadmin."""
    actor_id = UUID(current_user["sub"])
    return ClientesController(db).crear_cliente(body, actor_id)


@router.get("")
def listar_clientes(
    current_user: dict = Depends(require_superadmin()),
    db: Session = Depends(get_db),
):
    """Lista todos los clientes. Solo superadmin."""
    return ClientesController(db).listar_clientes()


@router.post("/{cliente_id}/renovar")
def renovar_cliente(
    cliente_id: UUID,
    current_user: dict = Depends(require_superadmin()),
    db: Session = Depends(get_db),
):
    """Registra renovación manual de un cliente. Solo superadmin."""
    actor_id = UUID(current_user["sub"])
    return ClientesController(db).renovar_cliente(cliente_id, actor_id)


@router.patch("/{cliente_id}/estado")
def cambiar_estado(
    cliente_id: UUID,
    body: CambiarEstadoRequest,
    current_user: dict = Depends(require_superadmin()),
    db: Session = Depends(get_db),
):
    """Pausa o reactiva un cliente. Solo superadmin."""
    actor_id = UUID(current_user["sub"])
    return ClientesController(db).cambiar_estado(cliente_id, body, actor_id)


@router.post("/{cliente_id}/marcas")
def crear_marca(
    cliente_id: UUID,
    body: CrearMarcaRequest,
    current_user: dict = Depends(require_admin_or_above()),
    db: Session = Depends(get_db),
):
    """Crea una marca dentro de un cliente."""
    actor_id = UUID(current_user["sub"])
    return ClientesController(db).crear_marca(cliente_id, body, actor_id)


@router.get("/{cliente_id}/marcas")
def listar_marcas(
    cliente_id: UUID,
    current_user: dict = Depends(require_admin_or_above()),
    db: Session = Depends(get_db),
):
    """Lista marcas de un cliente."""
    return ClientesController(db).listar_marcas(cliente_id)
