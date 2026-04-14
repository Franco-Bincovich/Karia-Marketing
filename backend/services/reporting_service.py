"""Servicio de Reporting — genera y envía reportes de datos puros."""
from __future__ import annotations

import logging
from datetime import date, timedelta
from uuid import UUID

from sqlalchemy.orm import Session

from middleware.audit import registrar_auditoria
from middleware.error_handler import AppError
from repositories import config_reportes_repository as config_repo
from repositories import kpis_repository as kpis_repo
from repositories import metricas_sociales_repository as metricas_repo
from repositories import reportes_repository as reportes_repo

logger = logging.getLogger(__name__)

_PERIODOS = {"diario": 1, "semanal": 7, "mensual": 30}


def generar_reporte(db: Session, marca_id: UUID, tipo: str) -> dict:
    """Genera reporte del período. Datos puros sin interpretación narrativa."""
    config = config_repo.obtener_o_crear(db, marca_id)
    dias = _PERIODOS.get(tipo, 7)
    fin = date.today()
    inicio = fin - timedelta(days=dias)

    totales = metricas_repo.total_periodo(db, marca_id, inicio, fin)
    kpis = kpis_repo.obtener_activos(db, marca_id)

    contenido = {"totales": totales, "kpis": kpis, "periodo": tipo}

    if config["incluir_comparacion"]:
        comp_inicio, comp_fin = _periodo_comparacion(inicio, fin, config["periodo_comparacion"])
        totales_ant = metricas_repo.total_periodo(db, marca_id, comp_inicio, comp_fin)
        variaciones = _calcular_variaciones(totales, totales_ant)
        contenido["comparacion"] = {"periodo_anterior": totales_ant, "variaciones": variaciones}

    formato = config["formatos"][0] if config["formatos"] else "panel"
    reporte = reportes_repo.crear(db, {
        "marca_id": marca_id, "tipo": tipo,
        "periodo_inicio": inicio, "periodo_fin": fin,
        "contenido": contenido, "formato": formato,
    })
    registrar_auditoria(
        db, accion="generar_reporte", modulo="analytics", marca_id=marca_id,
        recurso_id=reporte["id"], detalle={"tipo": tipo, "formato": formato},
    )
    db.commit()
    return reporte


def enviar_reporte(db: Session, reporte_id: UUID, marca_id: UUID) -> dict:
    """Envía reporte por el canal configurado. Mock para email/whatsapp."""
    reportes = reportes_repo.listar(db, marca_id)
    reporte = next((r for r in reportes if r["id"] == str(reporte_id)), None)
    if not reporte:
        raise AppError("Reporte no encontrado", "NOT_FOUND", 404)

    config = config_repo.obtener_o_crear(db, marca_id)
    canal = config["canal_notificacion"]
    logger.info(f"[reporting] enviar reporte {reporte_id} via {canal}")

    resultado = reportes_repo.marcar_enviado(db, reporte_id)
    registrar_auditoria(
        db, accion="enviar_reporte", modulo="analytics", marca_id=marca_id,
        recurso_id=str(reporte_id), detalle={"canal": canal, "formato": reporte["formato"]},
    )
    db.commit()
    return {**resultado, "canal_envio": canal}


def resumen_diario(db: Session, marca_id: UUID) -> dict:
    """Genera resumen del día para envío automático."""
    return generar_reporte(db, marca_id, "diario")


def _periodo_comparacion(inicio: date, fin: date, tipo: str):
    """Calcula el período de comparación según la configuración."""
    dias = (fin - inicio).days
    if tipo == "mes_anterior":
        return inicio - timedelta(days=30), fin - timedelta(days=30)
    if tipo == "mismo_periodo_anterior":
        return inicio - timedelta(days=365), fin - timedelta(days=365)
    return inicio - timedelta(days=dias), inicio  # semana_anterior default


def _calcular_variaciones(actual: dict, anterior: dict) -> dict:
    """Calcula variación porcentual entre dos períodos."""
    variaciones = {}
    for key in actual:
        val_act = actual[key]
        val_ant = anterior.get(key, 0)
        if val_ant > 0:
            variaciones[key] = round((val_act - val_ant) / val_ant * 100, 1)
        else:
            variaciones[key] = 100.0 if val_act > 0 else 0.0
    return variaciones
