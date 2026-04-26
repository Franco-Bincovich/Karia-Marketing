"""Servicio de monitoreo y métricas de campañas — Módulo Ads."""

from __future__ import annotations

import logging
from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from integrations import google_ads_client, meta_ads_client
from middleware.audit import registrar_auditoria
from middleware.error_handler import AppError
from repositories import campanas_repository as camp_repo
from repositories import metricas_ads_repository as metricas_repo
from repositories import umbrales_repository as umbrales_repo

logger = logging.getLogger(__name__)


def registrar_metricas(db: Session, campana_id: UUID, marca_id: UUID, access_token: str, fecha: date) -> dict:
    """Obtiene métricas de la API de la plataforma y las guarda."""
    obj = camp_repo.obtener(db, campana_id, marca_id)
    if not obj:
        raise AppError("Campaña no encontrada", "NOT_FOUND", 404)

    raw = _obtener_metricas_api(obj.plataforma, access_token, obj.campaign_id_externo or "mock", fecha.isoformat())
    clicks = raw["clicks"]
    impresiones = raw["impresiones"]
    conversiones = raw["conversiones"]
    gasto = raw["gasto"]

    data = {
        "campana_id": campana_id,
        "marca_id": marca_id,
        "fecha": fecha,
        "impresiones": impresiones,
        "clicks": clicks,
        "conversiones": conversiones,
        "gasto": Decimal(str(gasto)),
        "cpa": Decimal(str(round(gasto / conversiones, 2))) if conversiones else Decimal(0),
        "roas": Decimal(0),
        "ctr": Decimal(str(round(clicks / impresiones, 4))) if impresiones else Decimal(0),
    }
    resultado = metricas_repo.guardar_metricas(db, data)
    db.commit()
    return resultado


def verificar_umbrales(db: Session, marca_id: UUID, usuario_id: UUID, access_token: str, modo: str = "copilot") -> list:
    """
    Verifica CPA y ROAS de campañas activas contra umbrales.
    Autopilot: pausa automáticamente si se excede. Copilot: solo notifica.
    """
    umbrales = umbrales_repo.obtener_o_crear(db, marca_id)
    activas = camp_repo.listar_activas(db, marca_id)
    alertas = []

    for camp in activas:
        campana_id = UUID(camp["id"])
        totales = metricas_repo.calcular_totales(db, campana_id)
        alerta = _evaluar_campana(camp, totales, umbrales)
        if not alerta:
            continue

        registrar_auditoria(
            db,
            accion="alerta_umbral_ads",
            modulo="ads",
            usuario_id=usuario_id,
            marca_id=marca_id,
            recurso_id=camp["id"],
            detalle=alerta,
        )

        if modo == "autopilot" and alerta.get("requiere_pausa"):
            from services import campanas_service

            campanas_service.pausar_campana(
                db,
                campana_id,
                marca_id,
                usuario_id,
                access_token,
                motivo=f"autopilot: {alerta['motivo']}",
            )
            alerta["accion"] = "pausada_automaticamente"
        else:
            alerta["accion"] = "notificacion"

        alertas.append(alerta)

    if not alertas:
        db.commit()
    return alertas


def proyectar_gasto_mensual(db: Session, marca_id: UUID) -> dict:
    """Proyección de gasto al cierre del mes basada en el gasto acumulado."""
    hoy = date.today()
    dia_actual = hoy.day
    dias_mes = 30
    gasto_hoy = metricas_repo.gasto_diario_total(db, marca_id, hoy)
    activas = camp_repo.listar_activas(db, marca_id)
    presupuesto_diario_total = sum(c["presupuesto_diario"] for c in activas)
    proyeccion = presupuesto_diario_total * dias_mes
    return {
        "dia_actual": dia_actual,
        "gasto_hoy": gasto_hoy,
        "presupuesto_diario_total": presupuesto_diario_total,
        "proyeccion_mensual": round(proyeccion, 2),
        "campanas_activas": len(activas),
    }


def _evaluar_campana(camp: dict, totales: dict, umbrales: dict) -> dict:
    cpa = totales["cpa"]
    alertas_motivos = []
    if cpa > 0 and cpa > umbrales["cpa_maximo"]:
        alertas_motivos.append(f"CPA {cpa:.2f} > máx {umbrales['cpa_maximo']:.2f}")
    if not alertas_motivos:
        return {}
    return {
        "campana_id": camp["id"],
        "nombre": camp["nombre"],
        "motivo": "; ".join(alertas_motivos),
        "cpa_actual": cpa,
        "cpa_maximo": umbrales["cpa_maximo"],
        "requiere_pausa": True,
    }


def _obtener_metricas_api(plataforma: str, token: str, campaign_id: str, fecha: str) -> dict:
    if plataforma == "meta":
        return meta_ads_client.obtener_metricas(token, campaign_id, fecha)
    return google_ads_client.obtener_metricas(token, campaign_id, fecha)
