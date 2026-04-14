"""Modelos SQLAlchemy para el módulo de Comunidad y Social Listening."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from integrations.database import Base


def _now():
    return datetime.now(timezone.utc)


class MensajeComunidadMkt(Base):
    __tablename__ = "mensajes_comunidad_mkt"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    marca_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("marcas_mkt.id", ondelete="CASCADE"), nullable=False)
    red_social: Mapped[str] = mapped_column(Text, nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    autor_username: Mapped[Optional[str]] = mapped_column(Text)
    autor_id_externo: Mapped[Optional[str]] = mapped_column(Text)
    contenido: Mapped[str] = mapped_column(Text, nullable=False)
    clasificacion: Mapped[str] = mapped_column(String(25), default="consulta_comercial")
    sentimiento: Mapped[str] = mapped_column(String(10), default="neutro")
    respuesta: Mapped[Optional[str]] = mapped_column(Text)
    respondido: Mapped[bool] = mapped_column(Boolean, default=False)
    escalado: Mapped[bool] = mapped_column(Boolean, default=False)
    motivo_escalado: Mapped[Optional[str]] = mapped_column(Text)
    es_lead: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    respondido_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class ConfigComunidadMkt(Base):
    __tablename__ = "config_comunidad_mkt"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    marca_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("marcas_mkt.id", ondelete="CASCADE"), unique=True, nullable=False)
    criterios_escalado: Mapped[Optional[list]] = mapped_column(ARRAY(Text))
    tiempo_respuesta_max: Mapped[int] = mapped_column(Integer, default=120)
    responder_agresivos: Mapped[bool] = mapped_column(Boolean, default=False)
    responder_spam: Mapped[bool] = mapped_column(Boolean, default=False)
    modo: Mapped[str] = mapped_column(String(10), default="copilot")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class MencionMkt(Base):
    __tablename__ = "menciones_mkt"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    marca_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("marcas_mkt.id", ondelete="CASCADE"), nullable=False)
    tipo: Mapped[str] = mapped_column(String(15), nullable=False)
    fuente: Mapped[str] = mapped_column(Text, nullable=False)
    url: Mapped[Optional[str]] = mapped_column(Text)
    autor: Mapped[Optional[str]] = mapped_column(Text)
    contenido: Mapped[str] = mapped_column(Text, nullable=False)
    sentimiento: Mapped[str] = mapped_column(String(10), default="neutro")
    alcance_estimado: Mapped[int] = mapped_column(Integer, default=0)
    urgente: Mapped[bool] = mapped_column(Boolean, default=False)
    procesado: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class ConfigListeningMkt(Base):
    __tablename__ = "config_listening_mkt"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    marca_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("marcas_mkt.id", ondelete="CASCADE"), unique=True, nullable=False)
    terminos_marca: Mapped[Optional[list]] = mapped_column(ARRAY(Text))
    terminos_competidores: Mapped[Optional[list]] = mapped_column(ARRAY(Text))
    keywords_sector: Mapped[Optional[list]] = mapped_column(ARRAY(Text))
    notificar_negativas: Mapped[bool] = mapped_column(Boolean, default=True)
    notificar_competidores: Mapped[bool] = mapped_column(Boolean, default=True)
    umbral_urgencia: Mapped[int] = mapped_column(Integer, default=1000)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)
