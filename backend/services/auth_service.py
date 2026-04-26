"""Servicio de autenticación: login, logout, refresh y validación de permisos."""

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from config.settings import get_settings
from middleware.audit import registrar_auditoria
from middleware.error_handler import AppError
from repositories.auth_repository import AuthRepository
from repositories.permisos_repository import PermisosRepository
from utils.security import (
    create_access_token,
    decode_access_token,
    hash_token,
    verify_password,
)


class AuthService:
    """Lógica de negocio de autenticación y autorización."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = AuthRepository(db)
        self.permisos_repo = PermisosRepository(db)

    def login(self, email: str, password: str, ip: Optional[str] = None, user_agent: Optional[str] = None) -> dict:
        """Autentica un usuario y retorna token JWT + datos de sesión."""
        usuario = self.repo.get_usuario_by_email(email)
        if not usuario or not usuario.activo:
            raise AppError("Credenciales inválidas", "INVALID_CREDENTIALS", 401)

        if not verify_password(password, usuario.password_hash):
            raise AppError("Credenciales inválidas", "INVALID_CREDENTIALS", 401)

        settings = get_settings()
        payload = {
            "sub": str(usuario.id),
            "email": usuario.email,
            "rol": usuario.rol,
            "cliente_id": str(usuario.cliente_id),
        }
        token = create_access_token(payload)
        t_hash = hash_token(token)
        expires = datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRATION_HOURS)

        self.repo.create_sesion(
            {
                "usuario_id": usuario.id,
                "token_hash": t_hash,
                "ip": ip,
                "user_agent": user_agent,
                "expires_at": expires,
            }
        )

        registrar_auditoria(self.db, "login", "auth", usuario_id=usuario.id, ip=ip)
        self.db.commit()

        return {"access_token": token, "token_type": "bearer", "rol": usuario.rol}

    def logout(self, token: str, ip: Optional[str] = None) -> None:
        """Invalida la sesión asociada al token."""
        payload = decode_access_token(token)
        t_hash = hash_token(token)
        invalidated = self.repo.invalidate_sesion(t_hash)
        if not invalidated:
            raise AppError("Sesión no encontrada o ya cerrada", "SESSION_NOT_FOUND", 404)
        usuario_id = UUID(payload["sub"])
        registrar_auditoria(self.db, "logout", "auth", usuario_id=usuario_id, ip=ip)
        self.db.commit()

    def get_me(self, payload: dict) -> dict:
        """Retorna los datos del usuario autenticado."""
        usuario_id = UUID(payload["sub"])
        usuario = self.repo.get_usuario_by_id(usuario_id)
        if not usuario or not usuario.activo:
            raise AppError("Usuario no encontrado", "USER_NOT_FOUND", 404)
        return {
            "id": str(usuario.id),
            "email": usuario.email,
            "nombre": usuario.nombre,
            "rol": usuario.rol,
            "cliente_id": str(usuario.cliente_id),
        }

    def tiene_permiso(self, usuario_id: UUID, marca_id: UUID, modulo: str, accion: str) -> bool:
        """Verifica si un subusuario tiene un permiso específico."""
        permiso = self.permisos_repo.get_permiso(usuario_id, marca_id, modulo, accion)
        return bool(permiso and permiso.permitido)
