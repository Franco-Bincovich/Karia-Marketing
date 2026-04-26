"""Modelos SQLAlchemy para el módulo de Analytics y Reporting."""

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from integrations.database import Base


def _now():
    return datetime.now(timezone.utc)


class MetricasSocialesMkt(Base):
    __tablename__ = "metricas_sociales_mkt"
    __table_args__ = (UniqueConstraint("marca_id", "red_social", "fecha"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    marca_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("marcas_mkt.id", ondelete="CASCADE"), nullable=False)
    red_social: Mapped[str] = mapped_column(Text, nullable=False)
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    alcance: Mapped[int] = mapped_column(Integer, default=0)
    impresiones: Mapped[int] = mapped_column(Integer, default=0)
    engagement: Mapped[int] = mapped_column(Integer, default=0)
    engagement_rate: Mapped[Decimal] = mapped_column(Numeric(5, 4), default=0)
    nuevos_seguidores: Mapped[int] = mapped_column(Integer, default=0)
    clicks: Mapped[int] = mapped_column(Integer, default=0)
    reproducciones_video: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class KpiClienteMkt(Base):
    __tablename__ = "kpis_cliente_mkt"
    __table_args__ = (UniqueConstraint("marca_id", "kpi"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    marca_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("marcas_mkt.id", ondelete="CASCADE"), nullable=False)
    kpi: Mapped[str] = mapped_column(Text, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    valor_actual: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    valor_objetivo: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    periodo: Mapped[str] = mapped_column(String(10), default="mensual")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class ReporteMkt(Base):
    __tablename__ = "reportes_mkt"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    marca_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("marcas_mkt.id", ondelete="CASCADE"), nullable=False)
    tipo: Mapped[str] = mapped_column(String(10), nullable=False)
    periodo_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    periodo_fin: Mapped[date] = mapped_column(Date, nullable=False)
    contenido: Mapped[dict] = mapped_column(JSONB, nullable=False)
    resumen_ejecutivo: Mapped[Optional[str]] = mapped_column(Text)
    formato: Mapped[str] = mapped_column(String(10), nullable=False)
    enviado: Mapped[bool] = mapped_column(Boolean, default=False)
    enviado_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class AlertaMkt(Base):
    __tablename__ = "alertas_mkt"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    marca_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("marcas_mkt.id", ondelete="CASCADE"), nullable=False)
    tipo: Mapped[str] = mapped_column(Text, nullable=False)
    canal: Mapped[str] = mapped_column(String(10), default="panel")
    mensaje: Mapped[str] = mapped_column(Text, nullable=False)
    datos: Mapped[Optional[dict]] = mapped_column(JSONB)
    leida: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class ConfigReportesMkt(Base):
    __tablename__ = "config_reportes_mkt"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    marca_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("marcas_mkt.id", ondelete="CASCADE"), unique=True, nullable=False)
    frecuencia: Mapped[str] = mapped_column(String(10), default="semanal")
    formatos: Mapped[list] = mapped_column(ARRAY(Text), default=["panel"])
    canal_notificacion: Mapped[str] = mapped_column(String(10), default="panel")
    email_reporte: Mapped[Optional[str]] = mapped_column(Text)
    whatsapp_reporte: Mapped[Optional[str]] = mapped_column(Text)
    incluir_comparacion: Mapped[bool] = mapped_column(Boolean, default=True)
    periodo_comparacion: Mapped[str] = mapped_column(String(30), default="semana_anterior")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)
