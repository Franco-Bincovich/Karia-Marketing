"""Servicio de negocio para gestión de clientes, marcas y usuarios."""

import secrets
import string
from datetime import datetime, timedelta, timezone
from typing import List
from uuid import UUID

from sqlalchemy.orm import Session

from middleware.audit import registrar_auditoria
from middleware.error_handler import AppError
from repositories.auth_repository import AuthRepository
from repositories.clientes_repository import ClientesRepository
from utils.security import hash_password

CICLO_DIAS = 30
ALERTA_DIAS = 7


def _generate_temp_password(length: int = 12) -> str:
    """Genera una contraseña temporal segura."""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


class ClientesService:
    """Lógica de negocio para clientes, marcas y asignación de usuarios."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = ClientesRepository(db)
        self.auth_repo = AuthRepository(db)

    def crear_cliente(self, data: dict, actor_id: UUID) -> dict:
        """Crea un cliente nuevo y su usuario admin asociado. Solo superadmin."""
        if self.repo.get_cliente_by_email(data["email_admin"]):
            raise AppError("El email ya está registrado", "EMAIL_EXISTS", 409)
        if self.auth_repo.get_usuario_by_email(data["email_admin"]):
            raise AppError("El email ya tiene un usuario asociado", "EMAIL_EXISTS", 409)

        ahora = datetime.now(timezone.utc)
        cliente = self.repo.create_cliente({
            "nombre": data["nombre"],
            "email_admin": data["email_admin"],
            "pais": data.get("pais", "AR"),
            "plan": data.get("plan", "Basic"),
            "fecha_vencimiento": ahora + timedelta(days=CICLO_DIAS),
            "fecha_ultimo_pago": ahora,
        })
        self.db.flush()

        temp_password = _generate_temp_password()
        self.auth_repo.create_usuario({
            "email": data["email_admin"],
            "password_hash": hash_password(temp_password),
            "nombre": data["nombre"],
            "rol": "admin",
            "cliente_id": cliente.id,
        })

        from integrations.email_client import send_welcome_email
        send_welcome_email(data["email_admin"], temp_password, data["nombre"])

        registrar_auditoria(
            self.db, "crear_cliente", "clientes",
            usuario_id=actor_id, recurso_id=str(cliente.id),
        )
        self.db.commit()
        self.db.refresh(cliente)
        return _serialize_cliente(cliente)

    def listar_clientes(self) -> List[dict]:
        """Lista todos los clientes (activos y pausados)."""
        return [_serialize_cliente(c) for c in self.repo.list_clientes()]

    def cambiar_estado(self, cliente_id: UUID, activo: bool, actor_id: UUID) -> dict:
        """Pausa o reactiva un cliente."""
        cliente = self.repo.get_cliente_by_id(cliente_id)
        if not cliente:
            raise AppError("Cliente no encontrado", "CLIENT_NOT_FOUND", 404)
        cliente = self.repo.update_cliente(cliente_id, {"activo": activo})
        accion = "reactivar_cliente" if activo else "pausar_cliente"
        registrar_auditoria(
            self.db, accion, "clientes",
            usuario_id=actor_id, recurso_id=str(cliente_id),
        )
        self.db.commit()
        self.db.refresh(cliente)
        return _serialize_cliente(cliente)

    def renovar_cliente(self, cliente_id: UUID, actor_id: UUID) -> dict:
        """Registra pago manual y extiende membresía 30 días desde hoy."""
        cliente = self.repo.get_cliente_by_id(cliente_id)
        if not cliente:
            raise AppError("Cliente no encontrado", "CLIENT_NOT_FOUND", 404)

        ahora = datetime.now(timezone.utc)
        cliente = self.repo.update_cliente(cliente_id, {
            "fecha_ultimo_pago": ahora,
            "fecha_vencimiento": ahora + timedelta(days=CICLO_DIAS),
            "activo": True,
            "notificacion_enviada": False,
        })

        registrar_auditoria(
            self.db, "renovar_cliente", "clientes",
            usuario_id=actor_id, recurso_id=str(cliente_id),
        )
        self.db.commit()
        self.db.refresh(cliente)
        return _serialize_cliente(cliente)

    def crear_marca(self, cliente_id: UUID, data: dict, actor_id: UUID) -> dict:
        """Crea una marca asociada a un cliente e inicia onboarding + memoria."""
        if not self.repo.get_cliente_by_id(cliente_id):
            raise AppError("Cliente no encontrado", "CLIENT_NOT_FOUND", 404)
        data["cliente_id"] = cliente_id
        marca = self.repo.create_marca(data)
        registrar_auditoria(
            self.db, "crear_marca", "marcas",
            usuario_id=actor_id, cliente_id=cliente_id, recurso_id=str(marca.id),
        )
        self.db.flush()
        # Iniciar onboarding y memoria de marca automáticamente
        from services.onboarding_service import iniciar_onboarding
        iniciar_onboarding(self.db, marca.id)
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


def _calcular_estado_vencimiento(cliente) -> dict:
    """Calcula días restantes y estado de vencimiento."""
    ahora = datetime.now(timezone.utc)
    delta = cliente.fecha_vencimiento - ahora
    dias_restantes = max(0, delta.days)

    if not cliente.activo:
        estado = "vencido"
    elif dias_restantes <= 0:
        estado = "vencido"
    elif dias_restantes <= ALERTA_DIAS:
        estado = "por_vencer"
    else:
        estado = "activo"

    return {"dias_restantes": dias_restantes, "estado_vencimiento": estado}


def _serialize_cliente(c) -> dict:
    venc = _calcular_estado_vencimiento(c)
    return {
        "id": str(c.id),
        "nombre": c.nombre,
        "email_admin": c.email_admin,
        "pais": c.pais,
        "plan": c.plan,
        "activo": c.activo,
        "fecha_vencimiento": c.fecha_vencimiento.isoformat() if c.fecha_vencimiento else None,
        "fecha_ultimo_pago": c.fecha_ultimo_pago.isoformat() if c.fecha_ultimo_pago else None,
        "dias_restantes": venc["dias_restantes"],
        "estado_vencimiento": venc["estado_vencimiento"],
        "created_at": c.created_at.isoformat() if c.created_at else None,
    }


def _serialize_marca(m) -> dict:
    return {"id": str(m.id), "nombre": m.nombre, "cliente_id": str(m.cliente_id), "industria": m.industria, "activa": m.activa}


def _serialize_usuario(u) -> dict:
    return {"id": str(u.id), "email": u.email, "nombre": u.nombre, "rol": u.rol, "cliente_id": str(u.cliente_id), "activo": u.activo}
