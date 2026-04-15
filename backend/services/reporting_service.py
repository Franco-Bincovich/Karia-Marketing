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

    # Conteo de publicaciones del período
    from repositories import publicaciones_repository as pub_repo
    from repositories import contenido_repository as cont_repo
    from repositories import menciones_repository as menc_repo

    posts_count = 0
    contenido_count = 0
    menciones_count = menc_repo.total_menciones(db, marca_id)

    contenido_data = {"totales": totales, "kpis": kpis, "periodo": tipo,
                      "posts_publicados": posts_count, "contenido_generado": contenido_count,
                      "menciones": menciones_count}

    if config["incluir_comparacion"]:
        comp_inicio, comp_fin = _periodo_comparacion(inicio, fin, config["periodo_comparacion"])
        totales_ant = metricas_repo.total_periodo(db, marca_id, comp_inicio, comp_fin)
        variaciones = _calcular_variaciones(totales, totales_ant)
        contenido_data["comparacion"] = {"periodo_anterior": totales_ant, "variaciones": variaciones}

    # Generar resumen ejecutivo con Claude
    resumen = _generar_resumen_ejecutivo(contenido_data, tipo)

    formato = config["formatos"][0] if config["formatos"] else "panel"
    reporte = reportes_repo.crear(db, {
        "marca_id": marca_id, "tipo": tipo,
        "periodo_inicio": inicio, "periodo_fin": fin,
        "contenido": contenido_data, "resumen_ejecutivo": resumen,
        "formato": formato,
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


def _generar_resumen_ejecutivo(datos: dict, tipo: str) -> str:
    """Genera resumen ejecutivo del reporte con Claude."""
    try:
        from integrations.claude_client import _get_client, _SEARCH_MODEL
        import json
        client = _get_client()
        message = client.messages.create(
            model=_SEARCH_MODEL,
            max_tokens=500,
            system="Sos un analista de marketing. Generás resúmenes ejecutivos concisos y accionables.",
            messages=[{"role": "user", "content": (
                f"Generá un resumen ejecutivo de este reporte {tipo} de marketing.\n\n"
                f"Datos: {json.dumps(datos, default=str)}\n\n"
                f"El resumen debe: ser de 3-5 oraciones, destacar los insights más relevantes, "
                f"incluir una recomendación accionable. Respondé solo con el texto del resumen."
            )}],
        )
        blocks = [b for b in message.content if b.type == "text"]
        return blocks[-1].text.strip() if blocks else ""
    except Exception as e:
        logger.warning(f"[reporting] Error generando resumen: {e}")
        return ""


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
