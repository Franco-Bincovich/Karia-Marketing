"""Modelos SQLAlchemy para automatizaciones_mkt."""
from __future__ import annotations

import uuid
from typing import Optional
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from integrations.database import Base


def _now():
    return datetime.now(timezone.utc)


class AutomatizacionMkt(Base):
    __tablename__ = "automatizaciones_mkt"
    __table_args__ = (UniqueConstraint("marca_id", "tipo"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    marca_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("marcas_mkt.id", ondelete="CASCADE"), nullable=False)
    nombre: Mapped[str] = mapped_column(Text, nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    activa: Mapped[bool] = mapped_column(Boolean, default=True)
    ultima_ejecucion: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    proxima_ejecucion: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    intervalo_horas: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
