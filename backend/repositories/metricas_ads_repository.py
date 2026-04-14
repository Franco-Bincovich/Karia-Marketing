"""Repositorio para metricas_ads_mkt."""
from __future__ import annotations

import logging
from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.ads_models import MetricasAdsMkt

logger = logging.getLogger(__name__)


def _s(m: MetricasAdsMkt) -> dict:
    return {
        "id": str(m.id), "campana_id": str(m.campana_id),
        "ad_id": str(m.ad_id) if m.ad_id else None,
        "marca_id": str(m.marca_id), "fecha": m.fecha.isoformat(),
        "impresiones": m.impresiones, "clicks": m.clicks,
        "conversiones": m.conversiones, "gasto": float(m.gasto),
        "roas": float(m.roas), "cpa": float(m.cpa), "ctr": float(m.ctr),
    }


def guardar_metricas(db: Session, data: dict) -> dict:
    """Upsert: si ya existe registro para campana+ad+fecha, actualiza."""
    existing = db.query(MetricasAdsMkt).filter(
        MetricasAdsMkt.campana_id == data["campana_id"],
        MetricasAdsMkt.ad_id == data.get("ad_id"),
        MetricasAdsMkt.fecha == data["fecha"],
    ).first()
    if existing:
        for k, v in data.items():
            if hasattr(existing, k) and k != "id":
                setattr(existing, k, v)
        db.flush()
        return _s(existing)
    obj = MetricasAdsMkt(**data)
    db.add(obj)
    db.flush()
    return _s(obj)


def listar_por_campana(db: Session, campana_id: UUID) -> list:
    rows = (
        db.query(MetricasAdsMkt)
        .filter(MetricasAdsMkt.campana_id == campana_id)
        .order_by(MetricasAdsMkt.fecha.desc())
        .all()
    )
    return [_s(r) for r in rows]


def calcular_totales(db: Session, campana_id: UUID) -> dict:
    """Calcula totales acumulados de una campaña."""
    row = db.query(
        func.coalesce(func.sum(MetricasAdsMkt.impresiones), 0),
        func.coalesce(func.sum(MetricasAdsMkt.clicks), 0),
        func.coalesce(func.sum(MetricasAdsMkt.conversiones), 0),
        func.coalesce(func.sum(MetricasAdsMkt.gasto), Decimal(0)),
    ).filter(MetricasAdsMkt.campana_id == campana_id).first()
    gasto = float(row[3])
    conversiones = int(row[2])
    return {
        "impresiones": int(row[0]), "clicks": int(row[1]),
        "conversiones": conversiones, "gasto": gasto,
        "cpa": round(gasto / conversiones, 2) if conversiones else 0,
        "roas": 0,
    }


def gasto_diario_total(db: Session, marca_id: UUID, fecha: date) -> float:
    """Gasto total de todas las campañas de una marca en una fecha."""
    result = db.query(
        func.coalesce(func.sum(MetricasAdsMkt.gasto), Decimal(0))
    ).filter(
        MetricasAdsMkt.marca_id == marca_id,
        MetricasAdsMkt.fecha == fecha,
    ).scalar()
    return float(result)
