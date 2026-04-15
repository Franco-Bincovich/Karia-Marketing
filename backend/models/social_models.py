"""Modelos SQLAlchemy para el módulo de Calendario y Social Media."""
from __future__ import annotations

import uuid
from typing import Optional
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from integrations.database import Base


def _now():
    return datetime.now(timezone.utc)


class CalendarioEditorialMkt(Base):
    __tablename__ = "calendario_editorial_mkt"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    marca_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("marcas_mkt.id", ondelete="CASCADE"), nullable=False)
    cliente_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clientes_mkt.id", ondelete="CASCADE"), nullable=False)
    contenido_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("contenido_mkt.id", ondelete="SET NULL"))
    titulo: Mapped[str] = mapped_column(Text, nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text)
    red_social: Mapped[str] = mapped_column(String(30), nullable=False)
    formato: Mapped[str] = mapped_column(String(30), nullable=False)
    fecha_programada: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), default="programado")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class PublicacionesMkt(Base):
    __tablename__ = "publicaciones_mkt"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    marca_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("marcas_mkt.id", ondelete="CASCADE"), nullable=False)
    calendario_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("calendario_editorial_mkt.id", ondelete="SET NULL"))
    contenido_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("contenido_mkt.id", ondelete="SET NULL"))
    red_social: Mapped[str] = mapped_column(Text, nullable=False)
    post_id_externo: Mapped[Optional[str]] = mapped_column(Text)
    url_publicacion: Mapped[Optional[str]] = mapped_column(Text)
    copy_publicado: Mapped[Optional[str]] = mapped_column(Text)
    imagen_url: Mapped[Optional[str]] = mapped_column(Text)
    estado: Mapped[str] = mapped_column(String(20), default="publicado")
    intentos: Mapped[int] = mapped_column(Integer, default=1)
    error_detalle: Mapped[Optional[str]] = mapped_column(Text)
    likes_2hs: Mapped[int] = mapped_column(Integer, default=0)
    comentarios_2hs: Mapped[int] = mapped_column(Integer, default=0)
    alcance_2hs: Mapped[int] = mapped_column(Integer, default=0)
    engagement_bajo: Mapped[bool] = mapped_column(Boolean, default=False)
    programado_para: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    zernio_post_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    publicado_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class CuentasSocialesMkt(Base):
    __tablename__ = "cuentas_sociales_mkt"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    marca_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("marcas_mkt.id", ondelete="CASCADE"), nullable=False)
    red_social: Mapped[str] = mapped_column(String(30), nullable=False)
    nombre_cuenta: Mapped[str] = mapped_column(Text, nullable=False)
    account_id_externo: Mapped[Optional[str]] = mapped_column(Text)
    access_token_encrypted: Mapped[Optional[str]] = mapped_column(Text)
    token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    activa: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)
