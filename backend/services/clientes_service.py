"""Servicio de negocio para gestión de clientes, marcas y usuarios."""

from typing import List
from uuid import UUID

from sqlalchemy.orm import Session

from middleware.audit import registrar_auditoria
from middleware.error_handler import AppError
from repositories.auth_repository import AuthRepository
from repositories.clientes_repository import ClientesRepository
from utils.security import hash_password


class ClientesService:
    """Lógica de negocio para clientes, marcas y asignación de usuarios."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = ClientesRepository(db)
        self.auth_repo = AuthRepository(db)

    def crear_cliente(self, data: dict, actor_id: UUID) -> dict:
        """Crea un cliente nuevo. Solo superadmin."""
        if self.repo.get_cliente_by_email(data["email_admin"]):
            raise AppError("El email ya está registrado", "EMAIL_EXISTS", 409)
        cliente = self.repo.create_cliente(data)
        registrar_auditoria(
            self.db, "crear_cliente", "clientes",
            usuario_id=actor_id, recurso_id=str(cliente.id),
        )
        self.db.commit()
        self.db.refresh(cliente)
        return _serialize_cliente(cliente)

    def listar_clientes(self) -> List[dict]:
        """Lista todos los clientes activos."""
        return [_serialize_cliente(c) for c in self.repo.list_clientes()]

    def crear_marca(self, cliente_id: UUID, data: dict, actor_id: UUID) -> dict:
        """Crea una marca asociada a un cliente."""
        if not self.repo.get_cliente_by_id(cliente_id):
            raise AppError("Cliente no encontrado", "CLIENT_NOT_FOUND", 404)
        data["cliente_id"] = cliente_id
        marca = self.repo.create_marca(data)
        registrar_auditoria(
            self.db, "crear_marca", "marcas",
            usuario_id=actor_id, cliente_id=cliente_id, recurso_id=str(marca.id),
        )
        self.db.commit()
        self.db.refresh(marca)
        return _serialize_marca(marca)

    def listar_marcas(self, cliente_id: UUID) -> List[dict]:
        """Lista marcas activas de un cliente."""
        if not self.repo.get_cliente_by_id(cliente_id):
            raise AppError("Cliente no encontrado", "CLIENT_NOT_FOUND", 404)
        return [_serialize_marca(m) for m in self.repo.list_marcas_by_cliente(cliente_id)]

    def crear_usuario(self, data: dict, actor_id: UUID) -> dict:
        """Crea un usuario dentro de un cliente."""
        if self.auth_repo.get_usuario_by_email(data["email"]):
            raise AppError("Email ya registrado", "EMAIL_EXISTS", 409)
        data["password_hash"] = hash_password(data.pop("password"))
        usuario = self.auth_repo.create_usuario(data)
        registrar_auditoria(
            self.db, "crear_usuario", "usuarios",
            usuario_id=actor_id, cliente_id=usuario.cliente_id, recurso_id=str(usuario.id),
        )
        self.db.commit()
        self.db.refresh(usuario)
        return _serialize_usuario(usuario)

    def listar_usuarios(self, cliente_id: UUID) -> List[dict]:
        """Lista usuarios de un cliente."""
        return [_serialize_usuario(u) for u in self.auth_repo.list_usuarios_by_cliente(cliente_id)]

    def asignar_usuario_a_marca(self, usuario_id: UUID, marca_id: UUID, actor_id: UUID) -> dict:
        """Asigna un usuario a una marca."""
        asignacion = self.auth_repo.assign_marca(usuario_id, marca_id)
        registrar_auditoria(
            self.db, "asignar_usuario_marca", "usuarios",
            usuario_id=actor_id, recurso_id=str(asignacion.id),
        )
        self.db.commit()
        return {"usuario_id": str(usuario_id), "marca_id": str(marca_id)}


def _serialize_cliente(c) -> dict:
    return {"id": str(c.id), "nombre": c.nombre, "email_admin": c.email_admin, "pais": c.pais, "activo": c.activo}


def _serialize_marca(m) -> dict:
    return {"id": str(m.id), "nombre": m.nombre, "cliente_id": str(m.cliente_id), "industria": m.industria, "activa": m.activa}


def _serialize_usuario(u) -> dict:
    return {"id": str(u.id), "email": u.email, "nombre": u.nombre, "rol": u.rol, "cliente_id": str(u.cliente_id), "activo": u.activo}
