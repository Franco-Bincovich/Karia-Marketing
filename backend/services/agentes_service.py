"""Servicio de configuración y ejecución de agentes IA — Módulo 7."""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from middleware.error_handler import AppError
from models.agente_models import AgentesConfigMkt

logger = logging.getLogger(__name__)

# --- Definición de agentes ---

AGENTES = {
    "contenido": {
        "label": "Agente Contenido",
        "icon": "✍️",
        "rol": "Genera copies y variantes A/B/C",
        "prompt_base": "Sos el agente de contenido de {marca}. Tu función es generar copies creativos y efectivos para redes sociales basándote en el perfil de marca.",
        "bloqueado_v1": False,
        "solo_premium": False,
    },
    "social_media": {
        "label": "Agente Social Media",
        "icon": "📱",
        "rol": "Publica y monitorea redes",
        "prompt_base": "Sos el agente de social media de {marca}. Tu función es gestionar la publicación y el calendario editorial.",
        "bloqueado_v1": False,
        "solo_premium": False,
    },
    "comunidad": {
        "label": "Agente Comunidad",
        "icon": "💬",
        "rol": "Responde mensajes y DMs",
        "prompt_base": "Sos el agente de comunidad de {marca}. Tu función es responder mensajes y DMs de forma alineada a la voz de la marca.",
        "bloqueado_v1": False,
        "solo_premium": False,
    },
    "estrategia": {
        "label": "Agente Estrategia",
        "icon": "🧠",
        "rol": "Planifica y analiza competencia",
        "prompt_base": "Sos el agente de estrategia de {marca}. Tu función es analizar la competencia y proponer acciones estratégicas.",
        "bloqueado_v1": False,
        "solo_premium": False,
    },
    "creativo": {
        "label": "Agente Creativo",
        "icon": "🎨",
        "rol": "Genera imágenes con IA",
        "prompt_base": "Sos el agente creativo de {marca}. Tu función es generar imágenes y creativos visuales alineados a la identidad de la marca.",
        "bloqueado_v1": False,
        "solo_premium": False,
    },
    "reporting": {
        "label": "Agente Reporting",
        "icon": "📊",
        "rol": "Genera reportes periódicos",
        "prompt_base": "Sos el agente de reporting de {marca}. Tu función es generar reportes periódicos de performance.",
        "bloqueado_v1": False,
        "solo_premium": False,
    },
    "orquestador": {
        "label": "Agente Orquestador",
        "icon": "🎭",
        "rol": "Coordina todos los agentes activos",
        "prompt_base": "Sos el orquestador de {marca}. Tu función es coordinar todos los agentes activos y asegurar coherencia en las acciones.",
        "bloqueado_v1": False,
        "solo_premium": False,
    },
    "analytics": {
        "label": "Agente Analytics",
        "icon": "📈",
        "rol": "Consolida métricas y KPIs",
        "prompt_base": "Sos el agente de analytics de {marca}. Tu función es analizar métricas y KPIs de todas las plataformas conectadas.",
        "bloqueado_v1": False,
        "solo_premium": True,
    },
    "prospeccion": {
        "label": "Agente Prospección",
        "icon": "🎯",
        "rol": "Busca leads con IA",
        "prompt_base": "",
        "bloqueado_v1": True,
        "solo_premium": False,
    },
    "ads": {
        "label": "Agente Ads",
        "icon": "📣",
        "rol": "Gestiona campañas pagadas",
        "prompt_base": "",
        "bloqueado_v1": True,
        "solo_premium": False,
    },
    "seo": {
        "label": "Agente SEO",
        "icon": "🔍",
        "rol": "Investiga keywords y audita",
        "prompt_base": "",
        "bloqueado_v1": True,
        "solo_premium": False,
    },
    "listening": {
        "label": "Agente Listening",
        "icon": "👂",
        "rol": "Monitorea menciones y crisis",
        "prompt_base": "",
        "bloqueado_v1": True,
        "solo_premium": False,
    },
}

BLOQUEADOS_V1 = {k for k, v in AGENTES.items() if v["bloqueado_v1"]}
SOLO_PREMIUM = {k for k, v in AGENTES.items() if v["solo_premium"]}


def _get_plan(db: Session, marca_id: UUID) -> str:
    from models.cliente_models import ClienteMkt, MarcaMkt

    marca = db.query(MarcaMkt).filter(MarcaMkt.id == marca_id).first()
    if not marca:
        raise AppError("Marca no encontrada", "MARCA_NOT_FOUND", 404)
    cliente = db.query(ClienteMkt).filter(ClienteMkt.id == marca.cliente_id).first()
    if not cliente:
        raise AppError("Cliente no encontrado", "CLIENT_NOT_FOUND", 404)
    return cliente.plan or "Basic"


def _get_marca_nombre(db: Session, marca_id: UUID) -> str:
    from models.cliente_models import MarcaMkt

    marca = db.query(MarcaMkt).filter(MarcaMkt.id == marca_id).first()
    return marca.nombre if marca else "la marca"


def _estado_agente(nombre: str, plan: str, rol: str) -> str:
    """Calcula el estado de disponibilidad de un agente."""
    if rol == "superadmin":
        return "disponible"
    if nombre in BLOQUEADOS_V1:
        return "bloqueado_v1"
    if nombre in SOLO_PREMIUM and plan != "Premium":
        return "solo_premium"
    return "disponible"


def obtener_config(db: Session, marca_id: UUID, rol: str = "") -> list[dict]:
    """Retorna configuración de los 12 agentes con defaults si no existe config."""
    plan = _get_plan(db, marca_id)
    marca_nombre = _get_marca_nombre(db, marca_id)

    configs = (
        db.query(AgentesConfigMkt)
        .filter(
            AgentesConfigMkt.marca_id == marca_id,
        )
        .all()
    )
    config_map = {c.agente_nombre: c for c in configs}

    resultado = []
    for nombre, meta in AGENTES.items():
        config = config_map.get(nombre)
        estado = _estado_agente(nombre, plan, rol)
        prompt_base = meta["prompt_base"].replace("{marca}", marca_nombre)

        resultado.append(
            {
                "nombre": nombre,
                "label": meta["label"],
                "icon": meta["icon"],
                "rol": meta["rol"],
                "estado": estado,
                "activo": config.activo if config else (estado == "disponible"),
                "modo": config.modo if config else "copilot",
                "system_prompt": config.system_prompt_custom if config and config.system_prompt_custom else prompt_base,
                "system_prompt_default": prompt_base,
                "autopilot_disponible": plan == "Premium" or rol == "superadmin",
            }
        )

    return resultado


def actualizar_config(
    db: Session,
    marca_id: UUID,
    nombre: str,
    activo: Optional[bool] = None,
    modo: Optional[str] = None,
    system_prompt: Optional[str] = None,
    rol: str = "",
) -> dict:
    """Actualiza configuración de un agente."""
    if nombre not in AGENTES:
        raise AppError(f"Agente '{nombre}' no existe", "INVALID_AGENT", 400)

    plan = _get_plan(db, marca_id)
    estado = _estado_agente(nombre, plan, rol)

    if estado == "bloqueado_v1":
        raise AppError("Este agente no está disponible en V1", "AGENT_LOCKED", 423)
    if estado == "solo_premium":
        raise AppError("Este agente solo está disponible en Premium", "PLAN_LIMIT", 403)

    if modo == "autopilot" and plan != "Premium" and rol != "superadmin":
        raise AppError("Autopilot solo disponible en Premium", "PLAN_LIMIT", 403)

    config = (
        db.query(AgentesConfigMkt)
        .filter(
            AgentesConfigMkt.marca_id == marca_id,
            AgentesConfigMkt.agente_nombre == nombre,
        )
        .first()
    )

    if not config:
        config = AgentesConfigMkt(marca_id=marca_id, agente_nombre=nombre)
        db.add(config)
        db.flush()

    if activo is not None:
        config.activo = activo
    if modo is not None:
        config.modo = modo
    if system_prompt is not None:
        config.system_prompt_custom = system_prompt

    db.flush()
    db.commit()

    marca_nombre = _get_marca_nombre(db, marca_id)
    meta = AGENTES[nombre]
    prompt_base = meta["prompt_base"].replace("{marca}", marca_nombre)

    return {
        "nombre": nombre,
        "label": meta["label"],
        "icon": meta["icon"],
        "rol": meta["rol"],
        "estado": estado,
        "activo": config.activo,
        "modo": config.modo,
        "system_prompt": config.system_prompt_custom or prompt_base,
        "system_prompt_default": prompt_base,
        "autopilot_disponible": plan == "Premium" or rol == "superadmin",
    }


def ejecutar_agente(db: Session, marca_id: UUID, nombre: str, rol: str = "") -> dict:
    """Ejecuta la acción principal de un agente en modo Copilot."""
    if nombre not in AGENTES:
        raise AppError(f"Agente '{nombre}' no existe", "INVALID_AGENT", 400)

    plan = _get_plan(db, marca_id)
    estado = _estado_agente(nombre, plan, rol)

    if estado == "bloqueado_v1":
        raise AppError("Este agente no está disponible en V1", "AGENT_LOCKED", 423)
    if estado == "solo_premium":
        raise AppError("Este agente solo está disponible en Premium", "PLAN_LIMIT", 403)

    config = (
        db.query(AgentesConfigMkt)
        .filter(
            AgentesConfigMkt.marca_id == marca_id,
            AgentesConfigMkt.agente_nombre == nombre,
        )
        .first()
    )

    if config and not config.activo:
        raise AppError(f"El agente {nombre} está desactivado", "AGENT_INACTIVE", 400)

    marca_nombre = _get_marca_nombre(db, marca_id)
    from repositories import memoria_marca_repository as memoria_repo

    memoria_text = memoria_repo.obtener_para_agente(db, marca_id)

    meta = AGENTES[nombre]
    system_prompt = meta["prompt_base"].replace("{marca}", marca_nombre)
    if config and config.system_prompt_custom:
        system_prompt = config.system_prompt_custom

    # Dispatch especializados
    if nombre == "creativo":
        return _dispatch_creativo(db, marca_id, config, system_prompt)
    if nombre == "comunidad":
        return _dispatch_comunidad(db, marca_id)
    if nombre == "estrategia":
        return _dispatch_estrategia(db, marca_id)

    return _dispatch_agent(nombre, system_prompt, memoria_text, marca_nombre)


def _dispatch_creativo(db: Session, marca_id: UUID, config, system_prompt: str = "") -> dict:
    """Genera imagen real usando el servicio de imágenes."""
    from services import imagen_service

    modo = config.modo if config else "copilot"
    descripcion = system_prompt if system_prompt and system_prompt.strip() else "Imagen creativa para la próxima publicación de la marca"
    try:
        img = imagen_service.generar(
            db,
            marca_id,
            descripcion=descripcion,
            usar_perfil=True,
        )
        if modo == "autopilot":
            return {"agente": "creativo", "resultado": "Imagen generada y lista", "imagen": img}
        return {"agente": "creativo", "resultado": "Imagen generada para aprobación", "imagen": img}
    except Exception as e:
        return {"agente": "creativo", "resultado": f"Error al generar imagen: {str(e)}"}


def _dispatch_comunidad(db: Session, marca_id: UUID) -> dict:
    """Ejecuta revisión de mensajes pendientes y genera sugerencias."""
    from services import comunidad_service

    pendientes = comunidad_service.listar_pendientes(db, marca_id)
    if not pendientes:
        return {"agente": "comunidad", "resultado": "No hay mensajes pendientes de respuesta."}
    resumen = f"{len(pendientes)} mensajes pendientes.\n\n"
    for m in pendientes[:5]:
        resumen += f"- [{m['red_social']}] {m['autor_username'] or 'Anónimo'}: {m['contenido'][:80]}\n"
        if m.get("respuesta_sugerida"):
            resumen += f"  Sugerida: {m['respuesta_sugerida'][:80]}\n"
    return {"agente": "comunidad", "resultado": resumen, "pendientes": len(pendientes)}


def _dispatch_estrategia(db: Session, marca_id: UUID) -> dict:
    """Genera sugerencias estratégicas reales."""
    from services import estrategia_service

    entry = estrategia_service.sugerir_acciones(db, marca_id)
    contenido = entry.get("contenido", {})
    sugerencias = contenido.get("sugerencias", [])
    resumen = f"{len(sugerencias)} sugerencias generadas:\n\n"
    for s in sugerencias:
        titulo = s.get("titulo", "")
        desc = s.get("descripcion", "")
        prio = s.get("prioridad", "")
        resumen += f"- [{prio}] {titulo}: {desc[:100]}\n"
    return {"agente": "estrategia", "resultado": resumen, "estrategia_id": entry.get("id")}


def _dispatch_agent(nombre: str, system_prompt: str, memoria: str, marca_nombre: str) -> dict:
    """Despacha la ejecución al agente correspondiente."""
    from integrations.claude_client import _SEARCH_MODEL, _get_client

    user_prompt = _AGENT_PROMPTS.get(nombre, f"Ejecutá tu función principal para {marca_nombre}.")

    client = _get_client()
    message = client.messages.create(
        model=_SEARCH_MODEL,
        max_tokens=2048,
        system=f"{system_prompt}\n\nCONTEXTO DE MARCA:\n{memoria}",
        messages=[{"role": "user", "content": user_prompt}],
    )

    text_blocks = [b for b in message.content if b.type == "text"]
    if not text_blocks:
        return {"agente": nombre, "resultado": "Sin respuesta del agente"}

    return {"agente": nombre, "resultado": text_blocks[-1].text}


_AGENT_PROMPTS = {
    "contenido": "Proponé 3 ideas de contenido para la próxima semana. Para cada idea incluí: tema, red social, formato y un copy breve. Respondé en texto estructurado.",
    "social_media": "Analizá el estado actual del calendario editorial y sugerí acciones para los próximos 7 días. Respondé en texto estructurado.",
    "comunidad": "Revisá los patrones de mensajes recientes y sugerí respuestas tipo para las 3 consultas más frecuentes. Respondé en texto estructurado.",
    "estrategia": "Hacé un análisis rápido de la marca vs sus competidores y proponé 3 acciones estratégicas. Respondé en texto estructurado.",
    "creativo": "Proponé 3 conceptos visuales para el próximo contenido de la marca. Para cada uno describí: estilo, colores, composición. Respondé en texto estructurado.",
    "reporting": "Generá un resumen ejecutivo del estado actual de la marca con métricas clave y recomendaciones. Respondé en texto estructurado.",
    "orquestador": "Evaluá el estado de todos los agentes y proponé un plan de acción coordinado para esta semana. Respondé en texto estructurado.",
    "analytics": "Analizá las métricas disponibles y destacá los 3 insights más relevantes con recomendaciones accionables. Respondé en texto estructurado.",
}
