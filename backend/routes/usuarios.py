"""Rutas de gestión de usuarios y permisos."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from controllers.clientes_controller import ActualizarPermisoRequest, ClientesController, CrearUsuarioRequest
from integrations.database import get_db
from middleware.auth import get_current_user, require_admin_or_above

router = APIRouter(prefix="/api/usuarios", tags=["usuarios"])


@router.post("")
def crear_usuario(
    body: CrearUsuarioRequest,
    current_user: dict = Depends(require_admin_or_above()),
    db: Session = Depends(get_db),
):
    """Crea un nuevo usuario dentro de un cliente."""
    actor_id = UUID(current_user["sub"])
    return ClientesController(db).crear_usuario(body, actor_id)


@router.get("")
def listar_usuarios(
    cliente_id: UUID = Query(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista usuarios de un cliente. Admin ve solo su cliente; superadmin ve todos."""
    return ClientesController(db).listar_usuarios(cliente_id, current_user)


@router.patch("/{usuario_id}/permisos")
def actualizar_permisos(
    usuario_id: UUID,
    body: ActualizarPermisoRequest,
    current_user: dict = Depends(require_admin_or_above()),
    db: Session = Depends(get_db),
):
    """Actualiza o crea un permiso para un subusuario."""
    return ClientesController(db).actualizar_permiso(usuario_id, body)
