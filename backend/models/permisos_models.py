"""Modelos SQLAlchemy para permisos_mkt, feature_flags_mkt, onboarding_mkt y auditoria_mkt."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from integrations.database import Base


def _now():
    return datetime.now(timezone.utc)


class PermisoMkt(Base):
    __tablename__ = "permisos_mkt"
    __table_args__ = (UniqueConstraint("usuario_id", "marca_id", "modulo", "accion"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios_mkt.id", ondelete="CASCADE"), nullable=False)
    marca_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("marcas_mkt.id", ondelete="CASCADE"), nullable=False)
    modulo: Mapped[str] = mapped_column(Text, nullable=False)
    accion: Mapped[str] = mapped_column(Text, nullable=False)
    permitido: Mapped[bool] = mapped_column(Boolean, default=True)


class FeatureFlagMkt(Base):
    __tablename__ = "feature_flags_mkt"
    __table_args__ = (UniqueConstraint("cliente_id", "marca_id", "feature"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cliente_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clientes_mkt.id", ondelete="CASCADE"), nullable=False)
    marca_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("marcas_mkt.id", ondelete="CASCADE"))
    feature: Mapped[str] = mapped_column(Text, nullable=False)
    habilitado: Mapped[bool] = mapped_column(Boolean, default=True)
    modo: Mapped[str] = mapped_column(String(20), default="copilot")


class OnboardingMkt(Base):
    __tablename__ = "onboarding_mkt"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    marca_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("marcas_mkt.id", ondelete="CASCADE"), unique=True, nullable=False)
    paso_1_info_basica: Mapped[bool] = mapped_column(Boolean, default=False)
    paso_2_identidad_marca: Mapped[bool] = mapped_column(Boolean, default=False)
    paso_3_tono_voz: Mapped[bool] = mapped_column(Boolean, default=False)
    paso_4_audiencia: Mapped[bool] = mapped_column(Boolean, default=False)
    paso_5_competidores: Mapped[bool] = mapped_column(Boolean, default=False)
    paso_6_productos: Mapped[bool] = mapped_column(Boolean, default=False)
    paso_7_objetivos: Mapped[bool] = mapped_column(Boolean, default=False)
    paso_8_integraciones: Mapped[bool] = mapped_column(Boolean, default=False)
    paso_9_notificaciones: Mapped[bool] = mapped_column(Boolean, default=False)
    paso_10_subusuarios: Mapped[bool] = mapped_column(Boolean, default=False)
    completitud: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    marca = relationship("MarcaMkt", back_populates="onboarding")


class AuditoriaMkt(Base):
    __tablename__ = "auditoria_mkt"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios_mkt.id"))
    cliente_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("clientes_mkt.id"))
    marca_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("marcas_mkt.id"))
    accion: Mapped[str] = mapped_column(Text, nullable=False)
    modulo: Mapped[str] = mapped_column(Text, nullable=False)
    recurso_id: Mapped[str | None] = mapped_column(Text)
    detalle: Mapped[dict | None] = mapped_column(JSONB)
    ip: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
