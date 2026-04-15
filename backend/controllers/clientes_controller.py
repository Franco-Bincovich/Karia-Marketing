"""Adaptador HTTP para clientes_service y permisos."""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr

from middleware.error_handler import AppError
from repositories.permisos_repository import PermisosRepository
from services.clientes_service import ClientesService


class CrearClienteRequest(BaseModel):
    nombre: str
    email_admin: EmailStr
    pais: str = "AR"
    plan: str = "Basic"


class CambiarEstadoRequest(BaseModel):
    activo: bool


class CrearMarcaRequest(BaseModel):
    nombre: str
    industria: Optional[str] = None
    descripcion: Optional[str] = None
    sitio_web: Optional[str] = None


class CrearUsuarioRequest(BaseModel):
    email: EmailStr
    password: str
    nombre: str
    rol: str
    cliente_id: UUID


class ActualizarPermisoRequest(BaseModel):
    marca_id: UUID
    modulo: str
    accion: str
    permitido: bool


class FeatureFlagRequest(BaseModel):
    habilitado: bool
    modo: Optional[str] = "copilot"
    marca_id: Optional[UUID] = None


class ClientesController:
    """Convierte requests HTTP en llamadas al ClientesService."""

    def __init__(self, db):
        self.db = db
        self.service = ClientesService(db)
        self.permisos_repo = PermisosRepository(db)

    def crear_cliente(self, body: CrearClienteRequest, actor_id: UUID) -> dict:
        return self.service.crear_cliente(body.model_dump(), actor_id)

    def listar_clientes(self) -> List[dict]:
        return self.service.listar_clientes()

    def cambiar_estado(self, cliente_id: UUID, body: CambiarEstadoRequest, actor_id: UUID) -> dict:
        return self.service.cambiar_estado(cliente_id, body.activo, actor_id)

    def renovar_cliente(self, cliente_id: UUID, actor_id: UUID) -> dict:
        return self.service.renovar_cliente(cliente_id, actor_id)

    def crear_marca(self, cliente_id: UUID, body: CrearMarcaRequest, actor_id: UUID) -> dict:
        return self.service.crear_marca(cliente_id, body.model_dump(), actor_id)

    def listar_marcas(self, cliente_id: UUID) -> List[dict]:
        return self.service.listar_marcas(cliente_id)

    def crear_usuario(self, body: CrearUsuarioRequest, actor_id: UUID) -> dict:
        return self.service.crear_usuario(body.model_dump(), actor_id)

    def listar_usuarios(self, cliente_id: UUID, current_user: dict) -> List[dict]:
        rol = current_user.get("rol")
        cid = UUID(current_user["cliente_id"])
        if rol != "superadmin" and cid != cliente_id:
            raise AppError("Acceso denegado", "FORBIDDEN", 403)
        return self.service.listar_usuarios(cliente_id)

    def actualizar_permiso(self, usuario_id: UUID, body: ActualizarPermisoRequest) -> dict:
        permiso = self.permisos_repo.upsert_permiso(
            usuario_id, body.marca_id, body.modulo, body.accion, body.permitido
        )
        self.db.commit()
        return {"id": str(permiso.id), "permitido": permiso.permitido}

    def listar_feature_flags(self, cliente_id: UUID, marca_id: Optional[UUID]) -> List[dict]:
        flags = self.permisos_repo.list_feature_flags(cliente_id, marca_id)
        return [_serialize_flag(f) for f in flags]

    def actualizar_feature_flag(self, cliente_id: UUID, feature: str, body: FeatureFlagRequest) -> dict:
        data = body.model_dump(exclude_none=True)
        flag = self.permisos_repo.upsert_feature_flag(cliente_id, feature, data)
        self.db.commit()
        return _serialize_flag(flag)


def _serialize_flag(f) -> dict:
    return {
        "id": str(f.id),
        "feature": f.feature,
        "habilitado": f.habilitado,
        "modo": f.modo,
        "cliente_id": str(f.cliente_id),
        "marca_id": str(f.marca_id) if f.marca_id else None,
    }
