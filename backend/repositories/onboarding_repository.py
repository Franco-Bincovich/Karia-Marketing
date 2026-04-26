"""Repositorio para onboarding_mkt (tabla existente en permisos_models)."""

from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy.orm import Session

from models.onboarding_models import HistorialOnboardingMkt
from models.permisos_models import OnboardingMkt

logger = logging.getLogger(__name__)

_PASOS = [
    "paso_1_info_basica",
    "paso_2_identidad_marca",
    "paso_3_tono_voz",
    "paso_4_audiencia",
    "paso_5_competidores",
    "paso_6_productos",
    "paso_7_objetivos",
    "paso_8_integraciones",
    "paso_9_notificaciones",
    "paso_10_subusuarios",
]


def _s(o: OnboardingMkt) -> dict:
    """Serializa un OnboardingMkt a dict."""
    pasos = {p: getattr(o, p, False) for p in _PASOS}
    return {
        "id": str(o.id),
        "marca_id": str(o.marca_id),
        "pasos": pasos,
        "completitud": o.completitud,
        "respuestas": o.respuestas or {},
        "completado": o.completado or False,
        "updated_at": o.updated_at.isoformat() if o.updated_at else None,
    }


def obtener(db: Session, marca_id: UUID) -> dict:
    """Obtiene el estado del onboarding de una marca."""
    obj = db.query(OnboardingMkt).filter(OnboardingMkt.marca_id == marca_id).first()
    if not obj:
        obj = OnboardingMkt(marca_id=marca_id)
        db.add(obj)
        db.flush()
    return _s(obj)


def actualizar_paso(db: Session, marca_id: UUID, paso: int, completado: bool) -> dict:
    """Marca un paso como completado o no."""
    obj = db.query(OnboardingMkt).filter(OnboardingMkt.marca_id == marca_id).first()
    if not obj:
        obj = OnboardingMkt(marca_id=marca_id)
        db.add(obj)
        db.flush()
    campo = _PASOS[paso - 1] if 1 <= paso <= 10 else None
    if campo:
        setattr(obj, campo, completado)
    obj.completitud = calcular_completitud_obj(obj)
    db.flush()
    return _s(obj)


def calcular_completitud(db: Session, marca_id: UUID) -> int:
    """Calcula el porcentaje de completitud basado en los 10 pasos."""
    obj = db.query(OnboardingMkt).filter(OnboardingMkt.marca_id == marca_id).first()
    if not obj:
        return 0
    return calcular_completitud_obj(obj)


def calcular_completitud_obj(obj: OnboardingMkt) -> int:
    """Calcula completitud desde el objeto sin query extra."""
    completados = sum(1 for p in _PASOS if getattr(obj, p, False))
    return int(completados / len(_PASOS) * 100)


def actualizar_respuestas(db: Session, marca_id: UUID, respuestas: dict, completitud: int) -> dict:
    """Actualiza las respuestas del cuestionario y la completitud."""
    obj = db.query(OnboardingMkt).filter(OnboardingMkt.marca_id == marca_id).first()
    if not obj:
        obj = OnboardingMkt(marca_id=marca_id)
        db.add(obj)
        db.flush()
    obj.respuestas = respuestas
    obj.completitud = completitud
    db.flush()
    return _s(obj)


def marcar_completado(db: Session, marca_id: UUID) -> dict:
    """Marca el onboarding como completado."""
    obj = db.query(OnboardingMkt).filter(OnboardingMkt.marca_id == marca_id).first()
    if not obj:
        obj = OnboardingMkt(marca_id=marca_id)
        db.add(obj)
        db.flush()
    obj.completado = True
    obj.completitud = 100
    db.flush()
    return _s(obj)


def registrar_historial(db: Session, marca_id: UUID, paso: int, campo: str, valor_anterior: str, valor_nuevo: str, usuario_id: UUID) -> None:
    """Registra un cambio en el historial de onboarding."""
    obj = HistorialOnboardingMkt(
        marca_id=marca_id,
        paso=paso,
        campo=campo,
        valor_anterior=valor_anterior,
        valor_nuevo=valor_nuevo,
        modificado_por=usuario_id,
    )
    db.add(obj)
