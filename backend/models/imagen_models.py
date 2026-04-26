"""Modelos SQLAlchemy para imagenes_mkt."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from integrations.database import Base


def _now():
    return datetime.now(timezone.utc)


class ImagenMkt(Base):
    __tablename__ = "imagenes_mkt"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    marca_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("marcas_mkt.id", ondelete="CASCADE"), nullable=False)
    contenido_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("contenido_mkt.id", ondelete="SET NULL"))
    prompt: Mapped[Optional[str]] = mapped_column(Text)
    imagen_url: Mapped[str] = mapped_column(Text, nullable=False)
    tamano: Mapped[str] = mapped_column(String(20), default="1024x1024")
    estilo: Mapped[str] = mapped_column(String(20), default="vivid")
    origen: Mapped[str] = mapped_column(Text, default="ia")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
