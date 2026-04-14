"""Repositorio para kpis_cliente_mkt."""
from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy.orm import Session

from models.analytics_models import KpiClienteMkt

logger = logging.getLogger(__name__)

KPIS_DISPONIBLES = [
    "alcance_total", "engagement_rate", "nuevos_seguidores",
    "clicks_totales", "impresiones_totales", "reproducciones_video",
    "ctr_organico", "cpa_ads", "roas_ads", "gasto_ads",
    "conversiones_ads", "posicion_seo_promedio", "keywords_ranking",
    "publicaciones_totales", "contenido_aprobado", "leads_generados",
]


def _s(k: KpiClienteMkt) -> dict:
    """Serializa un KpiClienteMkt a dict."""
    return {
        "id": str(k.id), "marca_id": str(k.marca_id), "kpi": k.kpi,
        "activo": k.activo, "valor_actual": float(k.valor_actual),
        "valor_objetivo": float(k.valor_objetivo) if k.valor_objetivo else None,
        "periodo": k.periodo,
        "updated_at": k.updated_at.isoformat() if k.updated_at else None,
    }


def obtener_activos(db: Session, marca_id: UUID) -> list:
    """Lista KPIs activos de una marca."""
    rows = db.query(KpiClienteMkt).filter(
        KpiClienteMkt.marca_id == marca_id, KpiClienteMkt.activo == True,
    ).all()
    return [_s(r) for r in rows]


def actualizar_valor(db: Session, marca_id: UUID, kpi: str, valor: float) -> dict:
    """Actualiza el valor actual de un KPI, creándolo si no existe."""
    obj = db.query(KpiClienteMkt).filter(
        KpiClienteMkt.marca_id == marca_id, KpiClienteMkt.kpi == kpi,
    ).first()
    if not obj:
        obj = KpiClienteMkt(marca_id=marca_id, kpi=kpi, valor_actual=valor)
        db.add(obj)
    else:
        obj.valor_actual = valor
    db.flush()
    return _s(obj)


def activar_desactivar(db: Session, marca_id: UUID, kpi: str, activo: bool) -> dict:
    """Activa o desactiva un KPI para la marca."""
    obj = db.query(KpiClienteMkt).filter(
        KpiClienteMkt.marca_id == marca_id, KpiClienteMkt.kpi == kpi,
    ).first()
    if not obj:
        obj = KpiClienteMkt(marca_id=marca_id, kpi=kpi, activo=activo)
        db.add(obj)
    else:
        obj.activo = activo
    db.flush()
    return _s(obj)


def listar_todos_disponibles() -> list:
    """Retorna la lista de todos los KPIs posibles del sistema."""
    return list(KPIS_DISPONIBLES)
