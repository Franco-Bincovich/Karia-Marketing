"""Modelo SQLAlchemy para contactos_mkt."""
from __future__ import annotations

import uuid
from typing import Optional
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from integrations.database import Base


def _now():
    return datetime.now(timezone.utc)


class ContactoMkt(Base):
    __tablename__ = "contactos_mkt"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    marca_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("marcas_mkt.id", ondelete="CASCADE"), nullable=False
    )
    cliente_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clientes_mkt.id", ondelete="CASCADE"), nullable=False
    )
    nombre: Mapped[Optional[str]] = mapped_column(Text)
    empresa: Mapped[str] = mapped_column(Text, nullable=False)
    cargo: Mapped[Optional[str]] = mapped_column(Text)
    email_empresarial: Mapped[Optional[str]] = mapped_column(Text)
    email_personal: Mapped[Optional[str]] = mapped_column(Text)
    telefono_empresa: Mapped[Optional[str]] = mapped_column(Text)
    telefono_personal: Mapped[Optional[str]] = mapped_column(Text)
    linkedin_url: Mapped[Optional[str]] = mapped_column(Text)
    confianza: Mapped[int] = mapped_column(Integer, default=0)
    origen: Mapped[str] = mapped_column(String(20), default="ai")
    score: Mapped[int] = mapped_column(Integer, default=0)
    estado: Mapped[str] = mapped_column(String(20), default="nuevo")
    notas: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)
