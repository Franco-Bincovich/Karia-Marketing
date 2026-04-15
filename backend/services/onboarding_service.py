"""Servicio de Onboarding — cuestionario de 20 preguntas con asistencia IA para Premium."""
from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy.orm import Session

from middleware.error_handler import AppError
from repositories import memoria_marca_repository as memoria_repo
from repositories import onboarding_repository as onboarding_repo

logger = logging.getLogger(__name__)

# --- 20 preguntas iguales para todos los planes ---

PREGUNTAS = [
    {"id": 1, "seccion": "Marca", "pregunta": "¿Cuál es el nombre de tu marca y a qué se dedica?",
     "campos": ["nombre_marca", "descripcion"], "tipo": "texto", "obligatoria": True},
    {"id": 2, "seccion": "Audiencia", "pregunta": "¿A quién va dirigido tu producto o servicio?",
     "campos": ["publico_objetivo"], "tipo": "texto", "obligatoria": True},
    {"id": 3, "seccion": "Marca", "pregunta": "¿Qué problema resuelve tu marca?",
     "campos": ["propuesta_valor"], "tipo": "texto", "obligatoria": True},
    {"id": 4, "seccion": "Identidad", "pregunta": "¿Cuál es el tono de comunicación que usás?",
     "campos": ["tono_voz"], "tipo": "select", "obligatoria": True,
     "opciones": ["profesional", "cercano", "humoristico", "inspirador", "informativo", "urgente"]},
    {"id": 5, "seccion": "Marca", "pregunta": "¿Quiénes son tus principales competidores?",
     "campos": ["competidores"], "tipo": "texto", "obligatoria": True},
    {"id": 6, "seccion": "Marca", "pregunta": "¿Cuál es tu propuesta de valor diferencial?",
     "campos": ["diferenciadores"], "tipo": "texto", "obligatoria": False},
    {"id": 7, "seccion": "Marca", "pregunta": "¿Qué logros o resultados concretos ha tenido tu marca?",
     "campos": ["objetivos_periodo"], "tipo": "texto", "obligatoria": False},
    {"id": 8, "seccion": "Marca", "pregunta": "¿Cuáles son tus 3 productos o servicios principales?",
     "campos": ["productos_servicios"], "tipo": "texto", "obligatoria": False},
    {"id": 9, "seccion": "Marca", "pregunta": "¿Cuál es el rango de precios de tus productos/servicios?",
     "campos": ["icp_tamano_empresa"], "tipo": "texto", "obligatoria": False},
    {"id": 10, "seccion": "Contenido", "pregunta": "¿En qué canales digitales tenés presencia actualmente?",
     "campos": ["industria"], "tipo": "texto", "obligatoria": False},
    {"id": 11, "seccion": "Contenido", "pregunta": "¿Cuál es tu objetivo principal en redes sociales?",
     "campos": ["icp_descripcion"], "tipo": "texto", "obligatoria": False},
    {"id": 12, "seccion": "Contenido", "pregunta": "¿Qué tipo de contenido funciona mejor con tu audiencia?",
     "campos": ["ejemplos_contenido_aprobado"], "tipo": "texto", "obligatoria": False},
    {"id": 13, "seccion": "Contenido", "pregunta": "¿Qué contenido NO querés que se publique nunca?",
     "campos": ["politica_respuestas"], "tipo": "texto", "obligatoria": False},
    {"id": 14, "seccion": "Identidad", "pregunta": "¿Tenés alguna paleta de colores o guía de marca?",
     "campos": ["colores_marca", "tipografia"], "tipo": "texto", "obligatoria": False},
    {"id": 15, "seccion": "Identidad", "pregunta": "¿Qué palabras o frases representan tu marca?",
     "campos": ["palabras_clave"], "tipo": "texto", "obligatoria": False},
    {"id": 16, "seccion": "Identidad", "pregunta": "¿Qué palabras o frases NUNCA usarías?",
     "campos": ["palabras_prohibidas"], "tipo": "texto", "obligatoria": False},
    {"id": 17, "seccion": "Operación", "pregunta": "¿Cuál es la frecuencia ideal de publicación?",
     "campos": ["preguntas_frecuentes"], "tipo": "texto", "obligatoria": False},
    {"id": 18, "seccion": "Operación", "pregunta": "¿En qué horarios está más activa tu audiencia?",
     "campos": ["icp_cargo"], "tipo": "texto", "obligatoria": False},
    {"id": 19, "seccion": "Operación", "pregunta": "¿Hay algún evento, fecha o temporada importante para tu negocio?",
     "campos": ["icp_industria"], "tipo": "texto", "obligatoria": False},
    {"id": 20, "seccion": "Operación", "pregunta": "¿Algo más que quieras que el equipo de IA sepa sobre tu marca?",
     "campos": ["sitio_web"], "tipo": "texto", "obligatoria": False},
]

PREGUNTAS_OBLIGATORIAS = [p for p in PREGUNTAS if p["obligatoria"]]


def _get_plan(db: Session, marca_id: UUID) -> str:
    """Obtiene el plan del cliente a partir de la marca."""
    from models.cliente_models import ClienteMkt, MarcaMkt
    marca = db.query(MarcaMkt).filter(MarcaMkt.id == marca_id).first()
    if not marca:
        raise AppError("Marca no encontrada", "MARCA_NOT_FOUND", 404)
    cliente = db.query(ClienteMkt).filter(ClienteMkt.id == marca.cliente_id).first()
    if not cliente:
        raise AppError("Cliente no encontrado", "CLIENT_NOT_FOUND", 404)
    return cliente.plan or "Basic"


def iniciar_onboarding(db: Session, marca_id: UUID) -> dict:
    """Crea registro de onboarding y memoria de marca vacía."""
    onboarding = onboarding_repo.obtener(db, marca_id)
    memoria_repo.obtener_o_crear(db, marca_id)
    db.commit()
    return onboarding


def _ia_enabled(plan: str, rol: str = "") -> bool:
    """IA habilitada para Premium o superadmin."""
    return plan == "Premium" or rol == "superadmin"


def obtener_estado(db: Session, marca_id: UUID, rol: str = "") -> dict:
    """Retorna estado completo del onboarding — mismo cuestionario para todos los planes."""
    plan = _get_plan(db, marca_id)
    onboarding = onboarding_repo.obtener(db, marca_id)
    memoria = memoria_repo.obtener_o_crear(db, marca_id)
    completa = memoria_repo.esta_completa(db, marca_id)

    respuestas = onboarding.get("respuestas") or {}
    respondidas = sum(1 for p in PREGUNTAS if str(p["id"]) in respuestas and respuestas[str(p["id"])])
    total = len(PREGUNTAS)
    completitud_cuestionario = int(respondidas / total * 100) if total else 0

    return {
        **onboarding,
        "plan": plan,
        "ia_enabled": _ia_enabled(plan, rol),
        "preguntas": PREGUNTAS,
        "total_preguntas": total,
        "respondidas": respondidas,
        "completitud": completitud_cuestionario,
        "completado": onboarding.get("completado", False),
        "memoria": memoria,
        "memoria_completa": completa,
        "features_desbloqueados": completitud_cuestionario >= 80,
    }


def guardar_respuestas(db: Session, marca_id: UUID, respuestas: dict, usuario_id: UUID) -> dict:
    """Guarda progreso parcial del cuestionario."""
    ids_validos = {str(p["id"]) for p in PREGUNTAS}

    onboarding_actual = onboarding_repo.obtener(db, marca_id)
    existentes = onboarding_actual.get("respuestas") or {}
    for k, v in respuestas.items():
        if k in ids_validos:
            existentes[k] = v

    datos_memoria = _mapear_a_memoria(PREGUNTAS, existentes)
    if datos_memoria:
        memoria_repo.actualizar(db, marca_id, datos_memoria)

    respondidas = sum(1 for p in PREGUNTAS if str(p["id"]) in existentes and existentes[str(p["id"])])
    total = len(PREGUNTAS)
    completitud = int(respondidas / total * 100) if total else 0

    onboarding_repo.actualizar_respuestas(db, marca_id, existentes, completitud)
    db.commit()

    return obtener_estado(db, marca_id)


def completar_onboarding(db: Session, marca_id: UUID, usuario_id: UUID) -> dict:
    """Marca el onboarding como completo y consolida el perfil de marca."""
    onboarding = onboarding_repo.obtener(db, marca_id)
    respuestas = onboarding.get("respuestas") or {}

    faltantes = [p for p in PREGUNTAS_OBLIGATORIAS
                 if str(p["id"]) not in respuestas or not respuestas[str(p["id"])]]
    if faltantes:
        nombres = [p["pregunta"][:50] for p in faltantes]
        raise AppError(
            f"Faltan respuestas obligatorias: {', '.join(nombres)}",
            "INCOMPLETE_ONBOARDING", 400,
        )

    datos_memoria = _mapear_a_memoria(PREGUNTAS, respuestas)
    if datos_memoria:
        memoria_repo.actualizar(db, marca_id, datos_memoria)

    onboarding_repo.marcar_completado(db, marca_id)
    _desbloquear_features(db, marca_id)
    db.commit()

    return obtener_estado(db, marca_id)


def sugerir_respuesta(db: Session, marca_id: UUID, pregunta_id: int, rol: str = "") -> dict:
    """Usa Claude para sugerir una respuesta basada en el contexto ya respondido. Premium o superadmin."""
    plan = _get_plan(db, marca_id)
    if not _ia_enabled(plan, rol):
        raise AppError(
            "La asistencia de IA solo está disponible en el plan Premium",
            "PLAN_LIMIT", 403,
        )

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
    """Intenta autocompletar el perfil buscando info pública de la marca. Premium o superadmin."""
    plan = _get_plan(db, marca_id)
    if not _ia_enabled(plan, rol):
        raise AppError(
            "El autocompletado de IA solo está disponible en el plan Premium",
            "PLAN_LIMIT", 403,
        )

    from integrations.claude_client import autocompletar_perfil_marca
    sugerencias = autocompletar_perfil_marca(nombre_marca)

    # Merge sugerencias como respuestas
    onboarding = onboarding_repo.obtener(db, marca_id)
    existentes = onboarding.get("respuestas") or {}
    for k, v in sugerencias.items():
        if v and k not in existentes:
            existentes[k] = v

    datos_memoria = _mapear_a_memoria(PREGUNTAS, existentes)
    if datos_memoria:
        memoria_repo.actualizar(db, marca_id, datos_memoria)

    respondidas = sum(1 for p in PREGUNTAS if str(p["id"]) in existentes and existentes[str(p["id"])])
    total = len(PREGUNTAS)
    completitud = int(respondidas / total * 100) if total else 0

    onboarding_repo.actualizar_respuestas(db, marca_id, existentes, completitud)
    db.commit()

    return obtener_estado(db, marca_id)


def obtener_perfil(db: Session, marca_id: UUID) -> dict:
    """Retorna el perfil de marca consolidado usado por los agentes de IA."""
    memoria = memoria_repo.obtener_o_crear(db, marca_id)
    plan = _get_plan(db, marca_id)
    return {
        "plan": plan,
        "nombre_marca": memoria.get("nombre_marca"),
        "descripcion": memoria.get("descripcion"),
        "publico_objetivo": memoria.get("publico_objetivo"),
        "propuesta_valor": memoria.get("propuesta_valor"),
        "competidores": memoria.get("competidores"),
        "tono_voz": memoria.get("tono_voz"),
        "colores_marca": memoria.get("colores_marca", []),
        "tipografia": memoria.get("tipografia"),
        "palabras_clave": memoria.get("palabras_clave", []),
        "palabras_prohibidas": memoria.get("palabras_prohibidas", []),
        "productos_servicios": memoria.get("productos_servicios"),
        "diferenciadores": memoria.get("diferenciadores", []),
        "industria": memoria.get("industria"),
        "sitio_web": memoria.get("sitio_web"),
        "icp_descripcion": memoria.get("icp_descripcion"),
        "ejemplos_contenido_aprobado": memoria.get("ejemplos_contenido_aprobado", []),
        "politica_respuestas": memoria.get("politica_respuestas"),
        "objetivos_periodo": memoria.get("objetivos_periodo"),
        "updated_at": memoria.get("updated_at"),
    }


def regenerar_memoria(db: Session, marca_id: UUID) -> str:
    """Regenera el texto de memoria de marca para los agentes."""
    return memoria_repo.obtener_para_agente(db, marca_id)


# --- Legacy ---

def completar_paso(db: Session, marca_id: UUID, paso: int, datos: dict,
                   usuario_id: UUID) -> dict:
    """Completa un paso del onboarding legacy (10 pasos)."""
    _PASO_CAMPOS = {
        1: ["nombre_marca", "industria", "descripcion", "sitio_web"],
        2: ["propuesta_valor", "diferenciadores", "colores_marca", "tipografia"],
        3: ["tono_voz", "palabras_clave", "palabras_prohibidas", "ejemplos_contenido_aprobado"],
        4: ["publico_objetivo", "icp_descripcion", "icp_cargo", "icp_industria", "icp_tamano_empresa"],
        5: ["competidores"], 6: ["productos_servicios"], 7: ["objetivos_periodo"],
        8: [], 9: [], 10: [],
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
                db, marca_id, paso, campo, valor_anterior, valor_nuevo, usuario_id,
            )
    if datos_memoria:
        memoria_repo.actualizar(db, marca_id, datos_memoria)
    onboarding = onboarding_repo.actualizar_paso(db, marca_id, paso, True)
    if onboarding["completitud"] >= 80:
        _desbloquear_features(db, marca_id)
    db.commit()
    return onboarding


# --- Helpers ---

def _mapear_a_memoria(preguntas: list, respuestas: dict) -> dict:
    """Mapea respuestas del cuestionario a campos de memoria_marca."""
    datos = {}
    for p in preguntas:
        resp = respuestas.get(str(p["id"]))
        if not resp:
            continue
        campos = p["campos"]
        if len(campos) == 1:
            campo = campos[0]
            if campo in ("palabras_clave", "palabras_prohibidas", "colores_marca",
                         "diferenciadores", "ejemplos_contenido_aprobado",
                         "icp_cargo", "icp_industria"):
                datos[campo] = [x.strip() for x in resp.split(",") if x.strip()]
            elif campo in ("competidores", "productos_servicios", "objetivos_periodo",
                           "preguntas_frecuentes"):
                datos[campo] = {"respuesta": resp}
            else:
                datos[campo] = resp
        elif len(campos) == 2:
            partes = resp.split(".", 1)
            datos[campos[0]] = partes[0].strip()
            datos[campos[1]] = partes[1].strip() if len(partes) > 1 else resp
    return datos


def _desbloquear_features(db: Session, marca_id: UUID) -> None:
    """Desbloquea todos los features cuando el onboarding está completo."""
    from models.permisos_models import FeatureFlagMkt
    flags = db.query(FeatureFlagMkt).filter(FeatureFlagMkt.marca_id == marca_id).all()
    for flag in flags:
        flag.habilitado = True
    db.flush()
    logger.info("[onboarding_svc] features desbloqueados — marca=%s", marca_id)
