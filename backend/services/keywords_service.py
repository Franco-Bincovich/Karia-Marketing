"""Servicio de investigación y monitoreo de keywords — Módulo SEO."""
from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy.orm import Session

from integrations import semrush_client
from middleware.audit import registrar_auditoria
from repositories import config_seo_repository as config_repo
from repositories import keywords_repository as kw_repo

logger = logging.getLogger(__name__)

CAIDA_ALERTA = 3  # posiciones de caída para generar alerta


def investigar_keywords(db: Session, marca_id: UUID, query: str) -> list:
    """Busca keywords en Semrush y las guarda en keywords_mkt."""
    resultados_api = semrush_client.buscar_keywords(query)
    guardados = []
    for item in resultados_api:
        data = {
            "keyword": item["keyword"],
            "volumen_mensual": int(item.get("volumen_mensual", 0)),
            "dificultad": int(item.get("dificultad", 0)),
            "intencion": item.get("intencion", "informacional"),
            "estado": "oportunidad",
        }
        guardados.append(kw_repo.crear_o_actualizar(db, marca_id, data))
    db.commit()
    logger.debug(f"[keywords_svc] investigar — {len(guardados)} keywords guardadas")
    return guardados


def monitorear_posiciones(db: Session, marca_id: UUID) -> list:
    """Obtiene posiciones actuales y detecta caídas significativas."""
    config = config_repo.obtener_o_crear(db, marca_id)
    dominio = config.get("sitio_web", "")
    keywords = kw_repo.listar(db, marca_id)
    if not keywords or not dominio:
        return []

    kw_texts = [k["keyword"] for k in keywords]
    posiciones = semrush_client.obtener_posiciones(dominio, kw_texts)
    pos_map = {p["keyword"]: int(p.get("posicion", 0)) for p in posiciones}

    alertas = []
    for kw in keywords:
        nueva_pos = pos_map.get(kw["keyword"])
        if nueva_pos is None:
            continue
        kw_repo.actualizar_posicion(db, UUID(kw["id"]), nueva_pos)
        anterior = kw["posicion_actual"]
        if anterior and nueva_pos > anterior + CAIDA_ALERTA:
            alertas.append({
                "keyword": kw["keyword"], "anterior": anterior,
                "actual": nueva_pos, "caida": nueva_pos - anterior,
            })

    if alertas:
        registrar_auditoria(
            db, accion="alerta_caida_keywords", modulo="seo", marca_id=marca_id,
            detalle={"alertas": alertas, "total": len(alertas)},
        )
    db.commit()
    return alertas


def analizar_competidor(db: Session, marca_id: UUID, dominio_competidor: str) -> dict:
    """Identifica keywords del competidor que la marca no rankea."""
    config = config_repo.obtener_o_crear(db, marca_id)
    marca_dominio = config.get("sitio_web", "")
    resultado = semrush_client.analizar_competidor(dominio_competidor, marca_dominio)
    registrar_auditoria(
        db, accion="analizar_competidor_seo", modulo="seo", marca_id=marca_id,
        detalle={"competidor": dominio_competidor, "keywords_encontradas": len(resultado.get("keywords_exclusivas", []))},
    )
    db.commit()
    return resultado
