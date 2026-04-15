"""Modelos SQLAlchemy para el módulo de Contenido IA."""
from __future__ import annotations

import uuid
from typing import Optional
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from integrations.database import Base


def _now():
    return datetime.now(timezone.utc)


class ContenidoMkt(Base):
    __tablename__ = "contenido_mkt"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    marca_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("marcas_mkt.id", ondelete="CASCADE"), nullable=False)
    cliente_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clientes_mkt.id", ondelete="CASCADE"), nullable=False)
    red_social: Mapped[str] = mapped_column(String(30), nullable=False)
    formato: Mapped[str] = mapped_column(String(20), nullable=False)
    objetivo: Mapped[Optional[str]] = mapped_column(Text)
    tono: Mapped[Optional[str]] = mapped_column(Text)
    tema: Mapped[Optional[str]] = mapped_column(Text)
    copy_a: Mapped[Optional[str]] = mapped_column(Text)
    copy_b: Mapped[Optional[str]] = mapped_column(Text)
    copy_c: Mapped[Optional[str]] = mapped_column(Text)
    hashtags_a: Mapped[Optional[str]] = mapped_column(Text)
    hashtags_b: Mapped[Optional[str]] = mapped_column(Text)
    hashtags_c: Mapped[Optional[str]] = mapped_column(Text)
    cta_a: Mapped[Optional[str]] = mapped_column(Text)
    cta_b: Mapped[Optional[str]] = mapped_column(Text)
    cta_c: Mapped[Optional[str]] = mapped_column(Text)
    variante_seleccionada: Mapped[Optional[str]] = mapped_column(String(1))
    estado: Mapped[str] = mapped_column(String(30), default="borrador")
    modo: Mapped[str] = mapped_column(String(20), default="copilot")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    versiones = relationship("VersionesContenidoMkt", back_populates="contenido", cascade="all, delete-orphan")


class VersionesContenidoMkt(Base):
    __tablename__ = "versiones_contenido_mkt"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contenido_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("contenido_mkt.id", ondelete="CASCADE"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    copy_a: Mapped[Optional[str]] = mapped_column(Text)
    copy_b: Mapped[Optional[str]] = mapped_column(Text)
    copy_c: Mapped[Optional[str]] = mapped_column(Text)
    motivo_rechazo: Mapped[Optional[str]] = mapped_column(Text)
    creado_por: Mapped[str] = mapped_column(String(10), default="ia")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    contenido = relationship("ContenidoMkt", back_populates="versiones")


class AprendizajeMkt(Base):
    __tablename__ = "aprendizaje_mkt"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    marca_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("marcas_mkt.id", ondelete="CASCADE"), nullable=False)
    contenido_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("contenido_mkt.id"))
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    red_social: Mapped[Optional[str]] = mapped_column(Text)
    formato: Mapped[Optional[str]] = mapped_column(Text)
    tono: Mapped[Optional[str]] = mapped_column(Text)
    comentario: Mapped[Optional[str]] = mapped_column(Text)
    copy_original: Mapped[Optional[str]] = mapped_column(Text)
    copy_final: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class TemplatesMkt(Base):
    __tablename__ = "templates_mkt"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    marca_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("marcas_mkt.id", ondelete="CASCADE"), nullable=False)
    nombre: Mapped[str] = mapped_column(Text, nullable=False)
    red_social: Mapped[str] = mapped_column(Text, nullable=False)
    formato: Mapped[str] = mapped_column(Text, nullable=False)
    copy: Mapped[str] = mapped_column(Text, nullable=False)
    hashtags: Mapped[Optional[str]] = mapped_column(Text)
    tono: Mapped[Optional[str]] = mapped_column(Text)
    objetivo: Mapped[Optional[str]] = mapped_column(Text)
    usos: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
