"""Modelos SQLAlchemy para clientes_mkt y marcas_mkt."""
from __future__ import annotations

import uuid
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from integrations.database import Base


def _now():
    return datetime.now(timezone.utc)


class ClienteMkt(Base):
    __tablename__ = "clientes_mkt"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(Text, nullable=False)
    email_admin: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    pais: Mapped[str] = mapped_column(String(10), default="AR")
    plan: Mapped[str] = mapped_column(String(20), default="Basic")
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    fecha_vencimiento: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fecha_ultimo_pago: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    notificacion_enviada: Mapped[bool] = mapped_column(Boolean, default=False)
    anthropic_api_key_encrypted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    marcas = relationship("MarcaMkt", back_populates="cliente", cascade="all, delete-orphan")
    usuarios = relationship("UsuarioMkt", back_populates="cliente", cascade="all, delete-orphan")


class MarcaMkt(Base):
    __tablename__ = "marcas_mkt"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cliente_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clientes_mkt.id", ondelete="CASCADE"), nullable=False)
    nombre: Mapped[str] = mapped_column(Text, nullable=False)
    industria: Mapped[Optional[str]] = mapped_column(Text)
    descripcion: Mapped[Optional[str]] = mapped_column(Text)
    sitio_web: Mapped[Optional[str]] = mapped_column(Text)
    activa: Mapped[bool] = mapped_column(Boolean, default=True)
    onboarding_completitud: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    cliente = relationship("ClienteMkt", back_populates="marcas")
    onboarding = relationship("OnboardingMkt", back_populates="marca", uselist=False)
