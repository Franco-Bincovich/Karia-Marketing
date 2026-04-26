"""Modelos SQLAlchemy para el módulo de Ads (Meta Ads + Google Ads)."""

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from integrations.database import Base


def _now():
    return datetime.now(timezone.utc)


class CampanaAdsMkt(Base):
    __tablename__ = "campanas_ads_mkt"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    marca_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("marcas_mkt.id", ondelete="CASCADE"), nullable=False)
    cliente_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clientes_mkt.id", ondelete="CASCADE"), nullable=False)
    nombre: Mapped[str] = mapped_column(Text, nullable=False)
    plataforma: Mapped[str] = mapped_column(Text, nullable=False)
    objetivo: Mapped[Optional[str]] = mapped_column(Text)
    presupuesto_diario: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    presupuesto_mensual: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    campaign_id_externo: Mapped[Optional[str]] = mapped_column(Text)
    estado: Mapped[str] = mapped_column(String(30), default="borrador")
    aprobada_por: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios_mkt.id"))
    aprobada_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    ads = relationship("AdMkt", back_populates="campana", cascade="all, delete-orphan")


class AdMkt(Base):
    __tablename__ = "ads_mkt"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campana_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("campanas_ads_mkt.id", ondelete="CASCADE"), nullable=False)
    marca_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("marcas_mkt.id", ondelete="CASCADE"), nullable=False)
    nombre: Mapped[str] = mapped_column(Text, nullable=False)
    copy_titulo: Mapped[Optional[str]] = mapped_column(Text)
    copy_descripcion: Mapped[Optional[str]] = mapped_column(Text)
    imagen_url: Mapped[Optional[str]] = mapped_column(Text)
    ad_id_externo: Mapped[Optional[str]] = mapped_column(Text)
    variante: Mapped[str] = mapped_column(String(1), default="a")
    estado: Mapped[str] = mapped_column(String(20), default="activo")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    campana = relationship("CampanaAdsMkt", back_populates="ads")


class MetricasAdsMkt(Base):
    __tablename__ = "metricas_ads_mkt"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campana_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("campanas_ads_mkt.id", ondelete="CASCADE"), nullable=False)
    ad_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("ads_mkt.id", ondelete="CASCADE"))
    marca_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("marcas_mkt.id", ondelete="CASCADE"), nullable=False)
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    impresiones: Mapped[int] = mapped_column(Integer, default=0)
    clicks: Mapped[int] = mapped_column(Integer, default=0)
    conversiones: Mapped[int] = mapped_column(Integer, default=0)
    gasto: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    roas: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=0)
    cpa: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    ctr: Mapped[Decimal] = mapped_column(Numeric(5, 4), default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class UmbralesAdsMkt(Base):
    __tablename__ = "umbrales_ads_mkt"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    marca_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("marcas_mkt.id", ondelete="CASCADE"), unique=True, nullable=False)
    cpa_maximo: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=40.00)
    roas_minimo: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=2.50)
    gasto_diario_maximo: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=500.00)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)
