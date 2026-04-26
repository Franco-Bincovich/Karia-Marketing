"""Servicio de Onboarding — 15 obligatorias + ~20 opcionales, siempre editable."""

from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy.orm import Session

from middleware.error_handler import AppError
from repositories import memoria_marca_repository as memoria_repo
from repositories import onboarding_repository as onboarding_repo
from services.onboarding_preguntas import PREGUNTAS, PREGUNTAS_OBLIGATORIAS

logger = logging.getLogger(__name__)


# ── helpers ────────────────────────────────────────────────────


def _get_plan(db: Session, marca_id: UUID) -> str:
    from models.cliente_models import ClienteMkt, MarcaMkt

    marca = db.query(MarcaMkt).filter(MarcaMkt.id == marca_id).first()
    if not marca:
        raise AppError("Marca no encontrada", "MARCA_NOT_FOUND", 404)
    cliente = db.query(ClienteMkt).filter(ClienteMkt.id == marca.cliente_id).first()
    if not cliente:
        raise AppError("Cliente no encontrado", "CLIENT_NOT_FOUND", 404)
    return cliente.plan or "Basic"


def _ia_enabled(plan: str, rol: str = "") -> bool:
    return plan == "Premium" or rol == "superadmin"


def _completitud(preguntas: list, respuestas: dict) -> dict:
    """Calcula completitud total y de obligatorias por separado."""
    total = len(preguntas)
    respondidas = sum(1 for p in preguntas if str(p["id"]) in respuestas and respuestas[str(p["id"])])
    oblig = PREGUNTAS_OBLIGATORIAS
    oblig_resp = sum(1 for p in oblig if str(p["id"]) in respuestas and respuestas[str(p["id"])])
    return {
        "total": total,
        "respondidas": respondidas,
        "completitud": int(respondidas / total * 100) if total else 0,
        "obligatorias_total": len(oblig),
        "obligatorias_respondidas": oblig_resp,
        "obligatorias_completas": oblig_resp == len(oblig),
    }


# ── API pública ────────────────────────────────────────────────


def iniciar_onboarding(db: Session, marca_id: UUID) -> dict:
    onboarding = onboarding_repo.obtener(db, marca_id)
    memoria_repo.obtener_o_crear(db, marca_id)
    db.commit()
    return onboarding


def obtener_estado(db: Session, marca_id: UUID, rol: str = "") -> dict:
    plan = _get_plan(db, marca_id)
    onboarding = onboarding_repo.obtener(db, marca_id)
    memoria = memoria_repo.obtener_o_crear(db, marca_id)
    completa = memoria_repo.esta_completa(db, marca_id)

    respuestas = onboarding.get("respuestas") or {}
    stats = _completitud(PREGUNTAS, respuestas)

    return {
        **onboarding,
        "plan": plan,
        "ia_enabled": _ia_enabled(plan, rol),
        "preguntas": PREGUNTAS,
        **stats,
        "completado": onboarding.get("completado", False),
        "memoria": memoria,
        "memoria_completa": completa,
    }


def guardar_respuestas(db: Session, marca_id: UUID, respuestas: dict, usuario_id: UUID) -> dict:
    ids_validos = {str(p["id"]) for p in PREGUNTAS}

    onboarding_actual = onboarding_repo.obtener(db, marca_id)
    existentes = onboarding_actual.get("respuestas") or {}
    for k, v in respuestas.items():
        if k in ids_validos:
            existentes[k] = v

    datos_memoria = _mapear_a_memoria(PREGUNTAS, existentes)
    if datos_memoria:
        memoria_repo.actualizar(db, marca_id, datos_memoria)

    stats = _completitud(PREGUNTAS, existentes)
    onboarding_repo.actualizar_respuestas(db, marca_id, existentes, stats["completitud"])
    db.commit()

    return obtener_estado(db, marca_id)


def completar_onboarding(db: Session, marca_id: UUID, usuario_id: UUID) -> dict:
    """Marca onboarding como completo. Solo requiere las 15 obligatorias."""
    onboarding = onboarding_repo.obtener(db, marca_id)
    respuestas = onboarding.get("respuestas") or {}

    faltantes = [p for p in PREGUNTAS_OBLIGATORIAS if str(p["id"]) not in respuestas or not respuestas[str(p["id"])]]
    if faltantes:
        nombres = [p["pregunta"][:50] for p in faltantes]
        raise AppError(
            f"Faltan respuestas obligatorias: {', '.join(nombres)}",
            "INCOMPLETE_ONBOARDING",
            400,
        )

    datos_memoria = _mapear_a_memoria(PREGUNTAS, respuestas)
    if datos_memoria:
        memoria_repo.actualizar(db, marca_id, datos_memoria)

    onboarding_repo.marcar_completado(db, marca_id)
    _desbloquear_features(db, marca_id)
    db.commit()

    return obtener_estado(db, marca_id)


def sugerir_respuesta(db: Session, marca_id: UUID, pregunta_id: int, rol: str = "") -> dict:
    plan = _get_plan(db, marca_id)
    if not _ia_enabled(plan, rol):
        raise AppError("La asistencia de IA solo está disponible en el plan Premium", "PLAN_LIMIT", 403)

    pregunta = next((p for p in PREGUNTAS if p["id"] == pregunta_id), None)
    if not pregunta:
        raise AppError("Pregunta no encontrada", "INVALID_QUESTION", 400)

    onboarding = onboarding_repo.obtener(db, marca_id)
    respuestas = onboarding.get("respuestas") or {}
    memoria = memoria_repo.obtener_o_crear(db, marca_id)

    from integrations.claude_client import sugerir_respuesta_onboarding

    sugerencia = sugerir_respuesta_onboarding(
        pregunta=pregunta["pregunta"],
        contexto_respuestas=respuestas,
        preguntas=PREGUNTAS,
        memoria=memoria,
    )
    return {"pregunta_id": pregunta_id, "sugerencia": sugerencia}


def autocompletar_perfil(db: Session, marca_id: UUID, nombre_marca: str, rol: str = "") -> dict:
    plan = _get_plan(db, marca_id)
    if not _ia_enabled(plan, rol):
        raise AppError("El autocompletado de IA solo está disponible en el plan Premium", "PLAN_LIMIT", 403)

    from integrations.claude_client import autocompletar_perfil_marca

    sugerencias = autocompletar_perfil_marca(nombre_marca)

    onboarding = onboarding_repo.obtener(db, marca_id)
    existentes = onboarding.get("respuestas") or {}
    for k, v in sugerencias.items():
        if v and k not in existentes:
            existentes[k] = v

    datos_memoria = _mapear_a_memoria(PREGUNTAS, existentes)
    if datos_memoria:
        memoria_repo.actualizar(db, marca_id, datos_memoria)

    stats = _completitud(PREGUNTAS, existentes)
    onboarding_repo.actualizar_respuestas(db, marca_id, existentes, stats["completitud"])
    db.commit()

    return obtener_estado(db, marca_id)


def obtener_perfil(db: Session, marca_id: UUID) -> dict:
    memoria = memoria_repo.obtener_o_crear(db, marca_id)
    plan = _get_plan(db, marca_id)
    return {"plan": plan, **memoria, "documentos_adicionales": _get_documentos_texto(db, marca_id)}


def regenerar_memoria(db: Session, marca_id: UUID) -> str:
    return memoria_repo.obtener_para_agente(db, marca_id)


# ── Legacy (10 pasos) ─────────────────────────────────────────


def completar_paso(db: Session, marca_id: UUID, paso: int, datos: dict, usuario_id: UUID) -> dict:
    _PASO_CAMPOS = {
        1: ["nombre_marca", "industria", "descripcion", "sitio_web"],
        2: ["propuesta_valor", "diferenciadores", "colores_marca", "tipografia"],
        3: ["tono_voz", "palabras_clave", "palabras_prohibidas", "ejemplos_contenido_aprobado"],
        4: ["publico_objetivo", "icp_descripcion", "icp_cargo", "icp_industria", "icp_tamano_empresa"],
        5: ["competidores"],
        6: ["productos_servicios"],
        7: ["objetivos_periodo"],
        8: [],
        9: [],
        10: [],
    }
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
                db,
                marca_id,
                paso,
                campo,
                valor_anterior,
                valor_nuevo,
                usuario_id,
            )
    if datos_memoria:
        memoria_repo.actualizar(db, marca_id, datos_memoria)
    onboarding = onboarding_repo.actualizar_paso(db, marca_id, paso, True)
    db.commit()
    return onboarding


# ── Mapeo respuestas → memoria ─────────────────────────────────


def _mapear_a_memoria(preguntas: list, respuestas: dict) -> dict:
    """Mapea respuestas del cuestionario a campos de memoria_marca."""
    import re

    datos = {}
    _LISTA_CAMPOS = {
        "palabras_clave",
        "palabras_prohibidas",
        "diferenciadores",
        "ejemplos_contenido_aprobado",
        "icp_cargo",
        "icp_industria",
        "adjetivos_marca",
        "redes_activas",
    }
    _JSONB_CAMPOS = {
        "competidores",
        "productos_servicios",
        "objetivos_periodo",
        "preguntas_frecuentes",
    }

    for p in preguntas:
        resp = respuestas.get(str(p["id"]))
        if not resp:
            continue
        campos = p["campos"]
        if len(campos) == 1:
            campo = campos[0]
            if campo == "colores_marca":
                hexes = re.findall(r"#[0-9A-Fa-f]{6}", resp)
                datos[campo] = hexes if hexes else [resp.strip()] if resp.strip() else []
            elif campo in _LISTA_CAMPOS:
                datos[campo] = [x.strip() for x in resp.split(",") if x.strip()]
            elif campo in _JSONB_CAMPOS:
                datos[campo] = {"respuesta": resp}
            else:
                datos[campo] = resp
        elif len(campos) == 2:
            partes = resp.split(".", 1)
            val0 = partes[0].strip()
            val1 = partes[1].strip() if len(partes) > 1 else resp
            if campos[0] == "colores_marca":
                hexes = re.findall(r"#[0-9A-Fa-f]{6}", val0)
                datos[campos[0]] = hexes if hexes else ([val0] if val0 and val0.lower() not in ("sí", "si", "no") else [])
            else:
                datos[campos[0]] = val0
            datos[campos[1]] = val1
    return datos


def _get_documentos_texto(db: Session, marca_id: UUID) -> str:
    from services.documentos_service import obtener_textos

    return obtener_textos(db, marca_id)


def _desbloquear_features(db: Session, marca_id: UUID) -> None:
    from models.permisos_models import FeatureFlagMkt

    flags = db.query(FeatureFlagMkt).filter(FeatureFlagMkt.marca_id == marca_id).all()
    for flag in flags:
        flag.habilitado = True
    db.flush()
    logger.info("[onboarding_svc] features desbloqueados — marca=%s", marca_id)
