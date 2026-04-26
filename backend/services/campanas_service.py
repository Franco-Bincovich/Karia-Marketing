"""Servicio de campañas publicitarias — Módulo Ads."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from integrations import google_ads_client, meta_ads_client
from middleware.audit import registrar_auditoria
from middleware.error_handler import AppError
from repositories import campanas_repository as repo
from repositories import metricas_ads_repository as metricas_repo

logger = logging.getLogger(__name__)


def crear_campana(db: Session, marca_id: UUID, cliente_id: UUID, data: dict, usuario_id: UUID) -> dict:
    """Crea campaña en estado pendiente_aprobacion. Nunca se activa sin aprobación."""
    camp_data = {
        **data,
        "marca_id": marca_id,
        "cliente_id": cliente_id,
        "estado": "pendiente_aprobacion",
    }
    resultado = repo.crear(db, camp_data)
    registrar_auditoria(
        db,
        accion="crear_campana",
        modulo="ads",
        usuario_id=usuario_id,
        marca_id=marca_id,
        cliente_id=cliente_id,
        recurso_id=resultado["id"],
        detalle={"nombre": data["nombre"], "plataforma": data["plataforma"], "presupuesto_diario": float(data["presupuesto_diario"])},
    )
    db.commit()
    return resultado


def aprobar_campana(db: Session, campana_id: UUID, marca_id: UUID, usuario_id: UUID, access_token: str) -> dict:
    """Aprueba y activa una campaña. Requiere aprobación explícita."""
    obj = repo.obtener(db, campana_id, marca_id)
    if not obj:
        raise AppError("Campaña no encontrada", "NOT_FOUND", 404)
    if obj.estado != "pendiente_aprobacion":
        raise AppError(f"Solo campañas pendientes pueden aprobarse (estado actual: {obj.estado})", "INVALID_STATE", 400)

    api_result = _crear_en_plataforma(obj.plataforma, access_token, _to_api_data(obj))
    resultado = repo.actualizar_estado(
        db,
        campana_id,
        "activa",
        campaign_id_externo=api_result["campaign_id_externo"],
        aprobada_por=usuario_id,
        aprobada_at=datetime.now(timezone.utc),
    )
    registrar_auditoria(
        db,
        accion="aprobar_campana",
        modulo="ads",
        usuario_id=usuario_id,
        marca_id=marca_id,
        recurso_id=str(campana_id),
        detalle={"campaign_id_externo": api_result["campaign_id_externo"]},
    )
    db.commit()
    return resultado


def pausar_campana(db: Session, campana_id: UUID, marca_id: UUID, usuario_id: UUID, access_token: str, motivo: str = "manual") -> dict:
    """Pausa una campaña activa en la plataforma y en BD."""
    obj = repo.obtener(db, campana_id, marca_id)
    if not obj:
        raise AppError("Campaña no encontrada", "NOT_FOUND", 404)
    if obj.estado not in ("activa",):
        raise AppError("Solo campañas activas pueden pausarse", "INVALID_STATE", 400)

    _pausar_en_plataforma(obj.plataforma, access_token, obj.campaign_id_externo or "mock")
    resultado = repo.actualizar_estado(db, campana_id, "pausada")
    registrar_auditoria(
        db,
        accion="pausar_campana",
        modulo="ads",
        usuario_id=usuario_id,
        marca_id=marca_id,
        recurso_id=str(campana_id),
        detalle={"motivo": motivo},
    )
    db.commit()
    return resultado


def listar(db: Session, marca_id: UUID) -> list:
    return repo.listar(db, marca_id)


def obtener_con_metricas(db: Session, campana_id: UUID, marca_id: UUID) -> dict:
    obj = repo.obtener(db, campana_id, marca_id)
    if not obj:
        raise AppError("Campaña no encontrada", "NOT_FOUND", 404)
    from repositories import campanas_repository

    campana = campanas_repository._s(obj)
    campana["metricas"] = metricas_repo.calcular_totales(db, campana_id)
    return campana


def _to_api_data(obj) -> dict:
    return {
        "nombre": obj.nombre,
        "objetivo": obj.objetivo,
        "presupuesto_diario": str(obj.presupuesto_diario),
    }


def _crear_en_plataforma(plataforma: str, token: str, data: dict) -> dict:
    if plataforma == "meta":
        return meta_ads_client.crear_campana(token, "default", data)
    return google_ads_client.crear_campana(token, "default", data)


def _pausar_en_plataforma(plataforma: str, token: str, campaign_id: str) -> dict:
    if plataforma == "meta":
        return meta_ads_client.pausar_campana(token, campaign_id)
    return google_ads_client.pausar_campana(token, campaign_id)
