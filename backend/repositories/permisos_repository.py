"""Repositorio de acceso a datos para permisos_mkt y feature_flags_mkt."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from models.permisos_models import FeatureFlagMkt, PermisoMkt


class PermisosRepository:
    """CRUD puro sin lógica de negocio para permisos y feature flags."""

    def __init__(self, db: Session):
        self.db = db

    def get_permiso(self, usuario_id: UUID, marca_id: UUID, modulo: str, accion: str) -> Optional[PermisoMkt]:
        """Obtiene un permiso específico."""
        return (
            self.db.query(PermisoMkt)
            .filter(
                PermisoMkt.usuario_id == usuario_id,
                PermisoMkt.marca_id == marca_id,
                PermisoMkt.modulo == modulo,
                PermisoMkt.accion == accion,
            )
            .first()
        )

    def list_permisos_usuario(self, usuario_id: UUID) -> List[PermisoMkt]:
        """Lista todos los permisos de un usuario."""
        return self.db.query(PermisoMkt).filter(PermisoMkt.usuario_id == usuario_id).all()

    def upsert_permiso(self, usuario_id: UUID, marca_id: UUID, modulo: str, accion: str, permitido: bool) -> PermisoMkt:
        """Crea o actualiza un permiso."""
        permiso = self.get_permiso(usuario_id, marca_id, modulo, accion)
        if permiso:
            permiso.permitido = permitido
        else:
            permiso = PermisoMkt(
                usuario_id=usuario_id,
                marca_id=marca_id,
                modulo=modulo,
                accion=accion,
                permitido=permitido,
            )
            self.db.add(permiso)
        self.db.flush()
        return permiso

    def list_feature_flags(self, cliente_id: UUID, marca_id: Optional[UUID] = None) -> List[FeatureFlagMkt]:
        """Lista feature flags de un cliente, opcionalmente filtrado por marca."""
        query = self.db.query(FeatureFlagMkt).filter(FeatureFlagMkt.cliente_id == cliente_id)
        if marca_id:
            query = query.filter(FeatureFlagMkt.marca_id == marca_id)
        return query.all()

    def get_feature_flag(self, cliente_id: UUID, feature: str, marca_id: Optional[UUID] = None) -> Optional[FeatureFlagMkt]:
        """Obtiene un feature flag específico."""
        query = self.db.query(FeatureFlagMkt).filter(
            FeatureFlagMkt.cliente_id == cliente_id,
            FeatureFlagMkt.feature == feature,
        )
        if marca_id:
            query = query.filter(FeatureFlagMkt.marca_id == marca_id)
        return query.first()

    def upsert_feature_flag(self, cliente_id: UUID, feature: str, data: dict) -> FeatureFlagMkt:
        """Crea o actualiza un feature flag."""
        marca_id = data.get("marca_id")
        flag = self.get_feature_flag(cliente_id, feature, marca_id)
        if flag:
            for key, value in data.items():
                setattr(flag, key, value)
        else:
            flag = FeatureFlagMkt(cliente_id=cliente_id, feature=feature, **data)
            self.db.add(flag)
        self.db.flush()
        return flag
