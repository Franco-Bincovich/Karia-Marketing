"""Modelos SQLAlchemy para el módulo de SEO."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from integrations.database import Base


def _now():
    return datetime.now(timezone.utc)


class KeywordMkt(Base):
    __tablename__ = "keywords_mkt"
    __table_args__ = (UniqueConstraint("marca_id", "keyword"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    marca_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("marcas_mkt.id", ondelete="CASCADE"), nullable=False)
    keyword: Mapped[str] = mapped_column(Text, nullable=False)
    volumen_mensual: Mapped[int] = mapped_column(Integer, default=0)
    dificultad: Mapped[int] = mapped_column(Integer, default=0)
    intencion: Mapped[str] = mapped_column(String(20), default="informacional")
    posicion_actual: Mapped[Optional[int]] = mapped_column(Integer)
    posicion_anterior: Mapped[Optional[int]] = mapped_column(Integer)
    clicks_organicos: Mapped[int] = mapped_column(Integer, default=0)
    impresiones: Mapped[int] = mapped_column(Integer, default=0)
    ctr: Mapped[Decimal] = mapped_column(Numeric(5, 4), default=0)
    url_objetivo: Mapped[Optional[str]] = mapped_column(Text)
    estado: Mapped[str] = mapped_column(String(20), default="monitoreando")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class AuditoriaSeoMkt(Base):
    __tablename__ = "auditoria_seo_mkt"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    marca_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("marcas_mkt.id", ondelete="CASCADE"), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    severidad: Mapped[str] = mapped_column(String(10), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    recomendacion: Mapped[str] = mapped_column(Text, nullable=False)
    implementado: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class BriefSeoMkt(Base):
    __tablename__ = "briefs_seo_mkt"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    marca_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("marcas_mkt.id", ondelete="CASCADE"), nullable=False)
    keyword_principal: Mapped[str] = mapped_column(Text, nullable=False)
    keywords_secundarias: Mapped[Optional[str]] = mapped_column(Text)
    intencion_busqueda: Mapped[Optional[str]] = mapped_column(Text)
    estructura_sugerida: Mapped[Optional[str]] = mapped_column(Text)
    longitud_minima: Mapped[int] = mapped_column(Integer, default=800)
    competidores_url: Mapped[Optional[str]] = mapped_column(Text)
    meta_title: Mapped[Optional[str]] = mapped_column(Text)
    meta_description: Mapped[Optional[str]] = mapped_column(Text)
    usado: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class ConfigSeoMkt(Base):
    __tablename__ = "config_seo_mkt"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    marca_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("marcas_mkt.id", ondelete="CASCADE"), unique=True, nullable=False)
    sitio_web: Mapped[Optional[str]] = mapped_column(Text)
    frecuencia_reporte: Mapped[str] = mapped_column(String(15), default="semanal")
    semrush_proyecto_id: Mapped[Optional[str]] = mapped_column(Text)
    search_console_conectado: Mapped[bool] = mapped_column(Boolean, default=False)
    competidores: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)
