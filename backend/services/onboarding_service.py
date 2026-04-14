"""Servicio de Onboarding — flujo guiado de 10 pasos para configurar marca."""
from __future__ import annotations

import json
import logging
from uuid import UUID

from sqlalchemy.orm import Session

from middleware.error_handler import AppError
from repositories import memoria_marca_repository as memoria_repo
from repositories import onboarding_repository as onboarding_repo

logger = logging.getLogger(__name__)

_PASO_CAMPOS = {
    1: ["nombre_marca", "industria", "descripcion", "sitio_web"],
    2: ["propuesta_valor", "diferenciadores", "colores_marca", "tipografia"],
    3: ["tono_voz", "palabras_clave", "palabras_prohibidas", "ejemplos_contenido_aprobado"],
    4: ["publico_objetivo", "icp_descripcion", "icp_cargo", "icp_industria", "icp_tamano_empresa"],
    5: ["competidores"],
    6: ["productos_servicios"],
    7: ["objetivos_periodo"],
    8: [],  # integraciones — se configura en otros módulos
    9: [],  # notificaciones — se configura en config_reportes
    10: [],  # subusuarios — se configura en usuarios
}


def iniciar_onboarding(db: Session, marca_id: UUID) -> dict:
    """Crea registro de onboarding y memoria de marca vacía."""
    onboarding = onboarding_repo.obtener(db, marca_id)
    memoria_repo.obtener_o_crear(db, marca_id)
    db.commit()
    return onboarding


def completar_paso(db: Session, marca_id: UUID, paso: int, datos: dict,
                   usuario_id: UUID) -> dict:
    """Completa un paso del onboarding guardando datos en memoria de marca."""
    if paso < 1 or paso > 10:
        raise AppError("Paso debe estar entre 1 y 10", "INVALID_STEP", 400)

    campos = _PASO_CAMPOS.get(paso, [])
    memoria_actual = memoria_repo.obtener_o_crear(db, marca_id)

    datos_memoria = {}
    for campo in campos:
        if campo in datos:
            valor_anterior = str(memoria_actual.get(campo, ""))
            valor_nuevo = str(datos[campo]) if datos[campo] is not None else ""
            datos_memoria[campo] = datos[campo]
            onboarding_repo.registrar_historial(
                db, marca_id, paso, campo, valor_anterior, valor_nuevo, usuario_id,
            )

    if datos_memoria:
        memoria_repo.actualizar(db, marca_id, datos_memoria)

    onboarding = onboarding_repo.actualizar_paso(db, marca_id, paso, True)

    if onboarding["completitud"] >= 80:
        _desbloquear_features(db, marca_id)

    db.commit()
    return onboarding


def obtener_estado(db: Session, marca_id: UUID) -> dict:
    """Retorna estado completo del onboarding con memoria y features."""
    onboarding = onboarding_repo.obtener(db, marca_id)
    memoria = memoria_repo.obtener_o_crear(db, marca_id)
    completa = memoria_repo.esta_completa(db, marca_id)
    return {
        **onboarding,
        "memoria": memoria,
        "memoria_completa": completa,
        "features_desbloqueados": onboarding["completitud"] >= 80,
    }


def regenerar_memoria(db: Session, marca_id: UUID) -> str:
    """Regenera el texto de memoria de marca para los agentes."""
    return memoria_repo.obtener_para_agente(db, marca_id)


def _desbloquear_features(db: Session, marca_id: UUID) -> None:
    """Desbloquea todos los features cuando completitud >= 80%."""
    from models.permisos_models import FeatureFlagMkt
    flags = db.query(FeatureFlagMkt).filter(FeatureFlagMkt.marca_id == marca_id).all()
    for flag in flags:
        flag.habilitado = True
    db.flush()
    logger.info(f"[onboarding_svc] features desbloqueados — marca={marca_id}")
