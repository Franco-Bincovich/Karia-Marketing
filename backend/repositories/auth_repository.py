"""Repositorio de acceso a datos para usuarios_mkt y sesiones_mkt."""

from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from models.auth_models import SesionMkt, UsuarioMarcaMkt, UsuarioMkt


class AuthRepository:
    """CRUD puro sin lógica de negocio para usuarios y sesiones."""

    def __init__(self, db: Session):
        self.db = db

    def get_usuario_by_email(self, email: str) -> Optional[UsuarioMkt]:
        """Obtiene un usuario por email."""
        return self.db.query(UsuarioMkt).filter(UsuarioMkt.email == email).first()

    def get_usuario_by_id(self, usuario_id: UUID) -> Optional[UsuarioMkt]:
        """Obtiene un usuario por ID."""
        return self.db.query(UsuarioMkt).filter(UsuarioMkt.id == usuario_id).first()

    def create_usuario(self, data: dict) -> UsuarioMkt:
        """Crea un nuevo usuario."""
        usuario = UsuarioMkt(**data)
        self.db.add(usuario)
        self.db.flush()
        return usuario

    def update_usuario(self, usuario_id: UUID, data: dict) -> Optional[UsuarioMkt]:
        """Actualiza campos de un usuario."""
        usuario = self.get_usuario_by_id(usuario_id)
        if not usuario:
            return None
        for key, value in data.items():
            setattr(usuario, key, value)
        self.db.flush()
        return usuario

    def list_usuarios_by_cliente(self, cliente_id: UUID) -> List[UsuarioMkt]:
        """Lista todos los usuarios de un cliente."""
        return self.db.query(UsuarioMkt).filter(UsuarioMkt.cliente_id == cliente_id).all()

    def create_sesion(self, data: dict) -> SesionMkt:
        """Crea una nueva sesión activa."""
        sesion = SesionMkt(**data)
        self.db.add(sesion)
        self.db.flush()
        return sesion

    def invalidate_sesion(self, token_hash: str) -> bool:
        """Invalida una sesión por su token hash."""
        sesion = self.db.query(SesionMkt).filter(
            SesionMkt.token_hash == token_hash,
            SesionMkt.activa == True,  # noqa: E712
        ).first()
        if not sesion:
            return False
        sesion.activa = False
        self.db.flush()
        return True

    def get_sesion_activa(self, token_hash: str) -> Optional[SesionMkt]:
        """Obtiene una sesión activa y no expirada."""
        return self.db.query(SesionMkt).filter(
            SesionMkt.token_hash == token_hash,
            SesionMkt.activa == True,  # noqa: E712
            SesionMkt.expires_at > datetime.now(timezone.utc),
        ).first()

    def assign_marca(self, usuario_id: UUID, marca_id: UUID) -> UsuarioMarcaMkt:
        """Asigna una marca a un usuario."""
        asignacion = UsuarioMarcaMkt(usuario_id=usuario_id, marca_id=marca_id)
        self.db.add(asignacion)
        self.db.flush()
        return asignacion
