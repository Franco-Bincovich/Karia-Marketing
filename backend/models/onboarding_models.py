"""Modelos SQLAlchemy para Memoria de Marca e Historial de Onboarding."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from integrations.database import Base


def _now():
    return datetime.now(timezone.utc)


class MemoriaMarcaMkt(Base):
    __tablename__ = "memoria_marca_mkt"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    marca_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("marcas_mkt.id", ondelete="CASCADE"), unique=True, nullable=False)
    nombre_marca: Mapped[Optional[str]] = mapped_column(Text)
    industria: Mapped[Optional[str]] = mapped_column(Text)
    descripcion: Mapped[Optional[str]] = mapped_column(Text)
    propuesta_valor: Mapped[Optional[str]] = mapped_column(Text)
    productos_servicios: Mapped[Optional[dict]] = mapped_column(JSONB)
    publico_objetivo: Mapped[Optional[str]] = mapped_column(Text)
    tono_voz: Mapped[str] = mapped_column(String(15), default="profesional")
    palabras_clave: Mapped[Optional[list]] = mapped_column(ARRAY(Text))
    palabras_prohibidas: Mapped[Optional[list]] = mapped_column(ARRAY(Text))
    colores_marca: Mapped[Optional[list]] = mapped_column(ARRAY(Text))
    tipografia: Mapped[Optional[str]] = mapped_column(Text)
    ejemplos_contenido_aprobado: Mapped[Optional[list]] = mapped_column(ARRAY(Text))
    competidores: Mapped[Optional[dict]] = mapped_column(JSONB)
    diferenciadores: Mapped[Optional[list]] = mapped_column(ARRAY(Text))
    sitio_web: Mapped[Optional[str]] = mapped_column(Text)
    preguntas_frecuentes: Mapped[Optional[dict]] = mapped_column(JSONB)
    politica_respuestas: Mapped[Optional[str]] = mapped_column(Text)
    icp_descripcion: Mapped[Optional[str]] = mapped_column(Text)
    icp_cargo: Mapped[Optional[list]] = mapped_column(ARRAY(Text))
    icp_industria: Mapped[Optional[list]] = mapped_column(ARRAY(Text))
    icp_tamano_empresa: Mapped[Optional[str]] = mapped_column(Text)
    objetivos_periodo: Mapped[Optional[dict]] = mapped_column(JSONB)
    # Campos expandidos (migration 035)
    ciudad_zona: Mapped[Optional[str]] = mapped_column(Text)
    dolor_cliente: Mapped[Optional[str]] = mapped_column(Text)
    cta_principal: Mapped[Optional[str]] = mapped_column(Text)
    frecuencia_publicacion: Mapped[Optional[str]] = mapped_column(Text)
    aprobacion_contenido: Mapped[Optional[str]] = mapped_column(Text)
    redes_activas: Mapped[Optional[list]] = mapped_column(ARRAY(Text))
    adjetivos_marca: Mapped[Optional[list]] = mapped_column(ARRAY(Text))
    ventaja_competitiva: Mapped[Optional[str]] = mapped_column(Text)
    testimonios_resultados: Mapped[Optional[str]] = mapped_column(Text)
    temporada_alta_baja: Mapped[Optional[str]] = mapped_column(Text)
    fechas_especiales: Mapped[Optional[str]] = mapped_column(Text)
    tiene_fotos_propias: Mapped[Optional[str]] = mapped_column(Text)
    preferencia_imagenes: Mapped[Optional[str]] = mapped_column(Text)
    personalidad_marca: Mapped[Optional[str]] = mapped_column(Text)
    marcas_referencia: Mapped[Optional[str]] = mapped_column(Text)
    estetica_visual: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class HistorialOnboardingMkt(Base):
    __tablename__ = "historial_onboarding_mkt"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    marca_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("marcas_mkt.id", ondelete="CASCADE"), nullable=False)
    paso: Mapped[int] = mapped_column(Integer, nullable=False)
    campo: Mapped[str] = mapped_column(Text, nullable=False)
    valor_anterior: Mapped[Optional[str]] = mapped_column(Text)
    valor_nuevo: Mapped[Optional[str]] = mapped_column(Text)
    modificado_por: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios_mkt.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
