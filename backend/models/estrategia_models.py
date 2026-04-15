"""Modelos SQLAlchemy para estrategia_mkt."""
from __future__ import annotations

import uuid
from typing import Optional
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from integrations.database import Base


def _now():
    return datetime.now(timezone.utc)


class EstrategiaMkt(Base):
    __tablename__ = "estrategia_mkt"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    marca_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("marcas_mkt.id", ondelete="CASCADE"), nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    contenido: Mapped[dict] = mapped_column(JSONB, nullable=False)
    periodo: Mapped[Optional[str]] = mapped_column(Text)
    implementada: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
