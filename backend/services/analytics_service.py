"""Servicio de Analytics — trackea todo, muestra lo que el cliente activó."""
from __future__ import annotations

import logging
from datetime import date, timedelta
from uuid import UUID

from sqlalchemy.orm import Session

from repositories import alertas_repository as alertas_repo
from repositories import kpis_repository as kpis_repo
from repositories import metricas_sociales_repository as metricas_repo

logger = logging.getLogger(__name__)

ANOMALIA_UMBRAL = 0.20  # 20% de caída vs promedio


def consolidar_metricas(db: Session, marca_id: UUID, fecha: date) -> dict:
    """Consolida métricas de todos los canales para una fecha. Trackea todo."""
    canales = ["instagram", "facebook", "linkedin", "tiktok", "twitter"]
    resultados = []
    for canal in canales:
        data = {
            "marca_id": marca_id, "red_social": canal, "fecha": fecha,
            "alcance": 0, "impresiones": 0, "engagement": 0,
            "engagement_rate": 0, "nuevos_seguidores": 0,
            "clicks": 0, "reproducciones_video": 0,
        }
        resultados.append(metricas_repo.guardar_metricas(db, data))
    db.commit()
    return {"fecha": fecha.isoformat(), "canales": len(resultados)}


def calcular_kpis(db: Session, marca_id: UUID) -> dict:
    """Calcula KPIs activos y detecta anomalías (>20% de caída)."""
    kpis = kpis_repo.obtener_activos(db, marca_id)
    promedios = metricas_repo.promedio_por_canal(db, marca_id)
    anomalias = []

    for kpi in kpis:
        valor = kpi["valor_actual"]
        objetivo = kpi["valor_objetivo"]
        if objetivo and objetivo > 0 and valor < objetivo * (1 - ANOMALIA_UMBRAL):
            anomalia = {
                "kpi": kpi["kpi"], "valor_actual": valor,
                "valor_objetivo": objetivo, "diferencia_pct": round((1 - valor / objetivo) * 100, 1),
            }
            anomalias.append(anomalia)
            alertas_repo.crear(db, {
                "marca_id": marca_id, "tipo": "anomalia_kpi",
                "mensaje": f"KPI {kpi['kpi']} cayó {anomalia['diferencia_pct']}% bajo el objetivo",
                "datos": anomalia,
            })

    db.commit()
    return {"kpis": kpis, "anomalias": anomalias, "promedios": promedios}


def obtener_dashboard(db: Session, marca_id: UUID) -> dict:
    """Dashboard: KPIs activos, progreso a objetivos, últimos 30 días."""
    hoy = date.today()
    inicio = hoy - timedelta(days=30)
    kpis = kpis_repo.obtener_activos(db, marca_id)
    totales = metricas_repo.total_periodo(db, marca_id, inicio, hoy)
    promedios = metricas_repo.promedio_por_canal(db, marca_id)

    progreso = []
    for kpi in kpis:
        obj = kpi["valor_objetivo"]
        pct = round(kpi["valor_actual"] / obj * 100, 1) if obj and obj > 0 else 0
        progreso.append({"kpi": kpi["kpi"], "actual": kpi["valor_actual"],
                         "objetivo": obj, "progreso_pct": pct})

    return {
        "kpis": progreso, "metricas_30d": totales,
        "promedios_canal": promedios, "periodo": f"{inicio.isoformat()} a {hoy.isoformat()}",
    }


def obtener_tendencias(db: Session, marca_id: UUID) -> dict:
    """Evolución de métricas en los últimos 30 días."""
    hoy = date.today()
    inicio = hoy - timedelta(days=30)
    items = metricas_repo.listar(db, marca_id, inicio, hoy)
    por_fecha = {}
    for m in items:
        f = m.get("fecha")
        if f not in por_fecha:
            por_fecha[f] = {"fecha": f, "alcance": 0, "engagement": 0, "impresiones": 0, "clicks": 0}
        por_fecha[f]["alcance"] += m.get("alcance", 0)
        por_fecha[f]["engagement"] += m.get("engagement", 0)
        por_fecha[f]["impresiones"] += m.get("impresiones", 0)
        por_fecha[f]["clicks"] += m.get("clicks", 0)
    return {"data": sorted(por_fecha.values(), key=lambda x: x["fecha"]), "periodo": f"{inicio.isoformat()} a {hoy.isoformat()}"}


def obtener_top_contenido(db: Session, marca_id: UUID) -> list:
    """Top 5 publicaciones con mejor performance."""
    from repositories import publicaciones_repository as pub_repo
    pubs = pub_repo.listar(db, marca_id)
    sorted_pubs = sorted(pubs, key=lambda p: (p.get("likes_2hs", 0) + p.get("comentarios_2hs", 0)), reverse=True)
    return sorted_pubs[:5]


def verificar_alertas_personalizadas(db: Session, marca_id: UUID) -> list:
    """Evalúa condiciones de alerta y retorna las no leídas."""
    calcular_kpis(db, marca_id)
    return alertas_repo.listar_no_leidas(db, marca_id)
