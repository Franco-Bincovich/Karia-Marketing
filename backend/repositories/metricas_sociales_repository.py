"""Repositorio para metricas_sociales_mkt."""

from __future__ import annotations

import logging
from datetime import date
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.analytics_models import MetricasSocialesMkt

logger = logging.getLogger(__name__)


def _s(m: MetricasSocialesMkt) -> dict:
    """Serializa un MetricasSocialesMkt a dict."""
    return {
        "id": str(m.id),
        "marca_id": str(m.marca_id),
        "red_social": m.red_social,
        "fecha": m.fecha.isoformat(),
        "alcance": m.alcance,
        "impresiones": m.impresiones,
        "engagement": m.engagement,
        "engagement_rate": float(m.engagement_rate),
        "nuevos_seguidores": m.nuevos_seguidores,
        "clicks": m.clicks,
        "reproducciones_video": m.reproducciones_video,
    }


def guardar_metricas(db: Session, data: dict) -> dict:
    """Upsert: actualiza si ya existe registro para marca+red+fecha."""
    existing = (
        db.query(MetricasSocialesMkt)
        .filter(
            MetricasSocialesMkt.marca_id == data["marca_id"],
            MetricasSocialesMkt.red_social == data["red_social"],
            MetricasSocialesMkt.fecha == data["fecha"],
        )
        .first()
    )
    if existing:
        for k, v in data.items():
            if hasattr(existing, k) and k != "id":
                setattr(existing, k, v)
        db.flush()
        return _s(existing)
    obj = MetricasSocialesMkt(**data)
    db.add(obj)
    db.flush()
    return _s(obj)


def listar(db: Session, marca_id: UUID, fecha_inicio: date, fecha_fin: date) -> list:
    """Lista métricas de una marca en un rango de fechas."""
    rows = (
        db.query(MetricasSocialesMkt)
        .filter(
            MetricasSocialesMkt.marca_id == marca_id,
            MetricasSocialesMkt.fecha >= fecha_inicio,
            MetricasSocialesMkt.fecha <= fecha_fin,
        )
        .order_by(MetricasSocialesMkt.fecha.desc())
        .all()
    )
    return [_s(r) for r in rows]


def promedio_por_canal(db: Session, marca_id: UUID) -> dict:
    """Calcula promedio de engagement por canal."""
    rows = (
        db.query(
            MetricasSocialesMkt.red_social,
            func.avg(MetricasSocialesMkt.engagement),
            func.avg(MetricasSocialesMkt.alcance),
        )
        .filter(MetricasSocialesMkt.marca_id == marca_id)
        .group_by(MetricasSocialesMkt.red_social)
        .all()
    )
    return {r[0]: {"engagement_avg": float(r[1] or 0), "alcance_avg": float(r[2] or 0)} for r in rows}


def total_periodo(db: Session, marca_id: UUID, fecha_inicio: date, fecha_fin: date) -> dict:
    """Calcula totales acumulados de un período."""
    row = (
        db.query(
            func.coalesce(func.sum(MetricasSocialesMkt.alcance), 0),
            func.coalesce(func.sum(MetricasSocialesMkt.impresiones), 0),
            func.coalesce(func.sum(MetricasSocialesMkt.engagement), 0),
            func.coalesce(func.sum(MetricasSocialesMkt.clicks), 0),
            func.coalesce(func.sum(MetricasSocialesMkt.nuevos_seguidores), 0),
        )
        .filter(
            MetricasSocialesMkt.marca_id == marca_id,
            MetricasSocialesMkt.fecha >= fecha_inicio,
            MetricasSocialesMkt.fecha <= fecha_fin,
        )
        .first()
    )
    return {
        "alcance": int(row[0]),
        "impresiones": int(row[1]),
        "engagement": int(row[2]),
        "clicks": int(row[3]),
        "nuevos_seguidores": int(row[4]),
    }
