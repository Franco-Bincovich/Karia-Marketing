"""Servicio del Agente Estrategia — análisis de competencia, plan de contenido, sugerencias."""

import json
import logging
from uuid import UUID

from sqlalchemy.orm import Session

from integrations.claude_client import _SEARCH_MODEL, _WEB_SEARCH_TOOL, _get_client, _parse_json_object
from middleware.error_handler import AppError
from models.agente_models import AgentesConfigMkt
from repositories import estrategia_repository as repo
from repositories import memoria_marca_repository as memoria_repo

logger = logging.getLogger(__name__)

_DEFAULT_PLAN_PROMPT = (
    "Sos el Agente Estrategia de NEXO, una plataforma de marketing con IA para PyMEs.\n"
    "Tu rol es generar planes de contenido precisos, accionables y alineados al perfil\n"
    "real de la marca. Nunca inventás testimonios, casos de éxito ni métricas: solo\n"
    "usás los que el cliente proveyó explícitamente en su perfil.\n\n"
    'AGENTES DISPONIBLES EN NEXO (usá estos nombres exactos en el campo "agente"):\n'
    "- Agente Contenido: genera copies y variantes para posts y carruseles\n"
    "- Agente Creativo: genera imágenes con IA para el post\n"
    "- Agente Social Media: programa y publica en Instagram y Facebook\n"
    "- Agente Comunidad: responde comentarios y DMs relacionados al post\n"
    "- Agente Reporting: registra métricas del post publicado"
)

_DEFAULT_SUGERENCIAS_PROMPT = "Sos el agente de estrategia de {nombre}. Sugerís acciones concretas y priorizadas."


def _get_system_prompt(db: Session, marca_id: UUID, default_prompt: str) -> str:
    """Devuelve el system_prompt_custom de agentes_config_mkt para el agente 'estrategia',
    o default_prompt si no hay configuración personalizada."""
    config = (
        db.query(AgentesConfigMkt)
        .filter(
            AgentesConfigMkt.marca_id == marca_id,
            AgentesConfigMkt.agente_nombre == "estrategia",
        )
        .first()
    )
    if config and config.system_prompt_custom:
        return config.system_prompt_custom
    return default_prompt


def _get_memoria(db: Session, marca_id: UUID) -> str:
    return memoria_repo.obtener_para_agente(db, marca_id)


def analizar_competencia(db: Session, marca_id: UUID) -> dict:
    """Usa Claude con web search para investigar competidores del perfil de marca."""
    memoria = memoria_repo.obtener_o_crear(db, marca_id)
    competidores = memoria.get("competidores")
    nombre = memoria.get("nombre_marca", "la marca")

    comp_text = ""
    if isinstance(competidores, dict) and competidores.get("respuesta"):
        comp_text = competidores["respuesta"]
    elif isinstance(competidores, str):
        comp_text = competidores

    if not comp_text:
        raise AppError("No hay competidores definidos en el perfil de marca", "NO_COMPETITORS", 400)

    message = _get_client().messages.create(
        model=_SEARCH_MODEL,
        max_tokens=2048,
        tools=_WEB_SEARCH_TOOL,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Analizá los competidores de '{nombre}': {comp_text}\n\n"
                    f"Para cada competidor investigá:\n"
                    f"- Presencia en redes sociales\n"
                    f"- Tipo de contenido que publican\n"
                    f"- Frecuencia de publicación\n"
                    f"- Engagement aparente\n"
                    f"- Fortalezas y debilidades vs {nombre}\n\n"
                    f'Respondé con JSON: {{"competidores": [{{"nombre": ..., "redes": ..., '
                    f'"contenido": ..., "frecuencia": ..., "fortalezas": [...], '
                    f'"debilidades": [...], "oportunidades_para_{nombre}": [...]}}], '
                    f'"resumen": "..."}}'
                ),
            }
        ],
    )

    text_blocks = [b for b in message.content if b.type == "text"]
    try:
        resultado = _parse_json_object(text_blocks[-1].text) if text_blocks else {}
    except (ValueError, json.JSONDecodeError):
        resultado = {"resumen": text_blocks[-1].text if text_blocks else "Sin resultado"}

    entry = repo.crear(
        db,
        {
            "marca_id": marca_id,
            "tipo": "analisis",
            "contenido": resultado,
            "periodo": None,
        },
    )
    db.commit()
    return entry


def generar_plan_contenido(
    db: Session,
    marca_id: UUID,
    periodo: str = "semanal",
    red_social: str = "todas",
    formatos: list = None,
) -> dict:
    """Genera plan de contenido con filtros de red social y formatos."""
    memoria_text = _get_memoria(db, marca_id)
    memoria = memoria_repo.obtener_o_crear(db, marca_id)
    nombre = memoria.get("nombre_marca", "la marca")

    dias = {"diario": 7, "semanal": 7, "mensual": 30}.get(periodo, 7)
    formatos_permitidos = formatos or ["post", "carrusel", "reel", "story"]
    formatos_str = ", ".join(formatos_permitidos)

    red_instruccion = ""
    if red_social == "todas":
        red_instruccion = "Alterná entre Instagram y Facebook de forma equilibrada."
    else:
        red_instruccion = f"Todos los días deben ser para {red_social}."

    tiene_testimonios = bool(memoria.get("testimonios_resultados") and str(memoria.get("testimonios_resultados", "")).strip())
    if tiene_testimonios:
        testimonio_instruccion = (
            f"La marca tiene testimonios reales disponibles: "
            f"{memoria['testimonios_resultados']}. "
            f"Podés incluirlos en el plan cuando sea relevante."
        )
    else:
        testimonio_instruccion = (
            "La marca NO tiene testimonios cargados. "
            "PROHIBIDO inventar testimonios, casos de éxito o métricas de clientes. "
            "Si el plan incluye contenido de tipo testimonial, marcalo como "
            "'[PENDIENTE — el cliente debe proveer testimonio real]'."
        )

    system_prompt = _get_system_prompt(db, marca_id, _DEFAULT_PLAN_PROMPT)

    message = _get_client().messages.create(
        model=_SEARCH_MODEL,
        max_tokens=1600,
        system=(f"{system_prompt}\n\n" f"PERFIL DE MARCA:\n{memoria_text}\n\n" f"REGLA DE TESTIMONIOS:\n{testimonio_instruccion}"),
        messages=[
            {
                "role": "user",
                "content": (
                    f"Generá un plan de contenido de {dias} días para {nombre}.\n\n"
                    f"RESTRICCIONES:\n"
                    f"- Redes habilitadas: {red_instruccion}\n"
                    f"- Formatos permitidos: {formatos_str}\n"
                    f"- No uses formatos ni redes que no estén en la lista anterior\n\n"
                    f"INSTRUCCIÓN DE AGENTE:\n"
                    f"Para cada día del plan, asigná el agente de NEXO que ejecuta esa publicación.\n"
                    f"Usá exactamente uno de los nombres del listado del system prompt.\n\n"
                    f"Respondé ÚNICAMENTE con este JSON, sin texto adicional, sin markdown:\n"
                    f"{{\n"
                    f'  "resumen": "párrafo de 2-3 oraciones explicando la estrategia general del plan '
                    f'y cómo impacta en el objetivo del negocio de {nombre}",\n'
                    f'  "impacto_esperado": "1 oración sobre el resultado esperado al finalizar el '
                    f'periodo si se ejecuta el plan completo",\n'
                    f'  "plan": [\n'
                    f"    {{\n"
                    f'      "dia": 1,\n'
                    f'      "red_social": "instagram|facebook",\n'
                    f'      "formato": "post|story|reel|carrusel",\n'
                    f'      "tema": "tema concreto del contenido",\n'
                    f'      "objetivo": "qué se busca lograr con esta publicación",\n'
                    f'      "copy_sugerido": "copy breve listo para usar",\n'
                    f'      "agente": "nombre exacto del agente de NEXO que ejecuta esto"\n'
                    f"    }}\n"
                    f"  ]\n"
                    f"}}"
                ),
            }
        ],
    )

    text_blocks = [b for b in message.content if b.type == "text"]
    try:
        resultado = _parse_json_object(text_blocks[-1].text) if text_blocks else {}
    except (ValueError, json.JSONDecodeError):
        resultado = {"resumen": text_blocks[-1].text if text_blocks else "Sin resultado"}

    entry = repo.crear(
        db,
        {
            "marca_id": marca_id,
            "tipo": "plan",
            "contenido": resultado,
            "periodo": periodo,
        },
    )
    db.commit()
    return entry


def activar_plan(db: Session, marca_id: UUID, plan_id: UUID) -> dict:
    """Activa un plan y desactiva los anteriores."""
    result = repo.activar_plan(db, plan_id, marca_id)
    if not result:
        from middleware.error_handler import AppError

        raise AppError("Plan no encontrado", "NOT_FOUND", 404)
    db.commit()
    return result


def obtener_plan_activo(db: Session, marca_id: UUID) -> dict:
    """Retorna el plan de contenido activo de la marca."""
    return repo.obtener_plan_activo(db, marca_id)


def sugerir_acciones(db: Session, marca_id: UUID) -> dict:
    """Sugiere acciones estratégicas basadas en el perfil de marca."""
    memoria_text = _get_memoria(db, marca_id)
    memoria = memoria_repo.obtener_o_crear(db, marca_id)
    nombre = memoria.get("nombre_marca", "la marca")

    system_prompt = _get_system_prompt(db, marca_id, _DEFAULT_SUGERENCIAS_PROMPT).replace("{nombre}", nombre)

    message = _get_client().messages.create(
        model=_SEARCH_MODEL,
        max_tokens=1500,
        system=f"{system_prompt}\n\nPERFIL DE MARCA:\n{memoria_text}",
        messages=[
            {
                "role": "user",
                "content": (
                    f"Proponé 5 acciones estratégicas concretas para {nombre} basándote "
                    f"en su perfil de marca.\n\n"
                    f"Para cada acción incluí: título, descripción, prioridad (alta/media/baja), "
                    f"plazo estimado, impacto esperado.\n\n"
                    f'Respondé con JSON: {{"sugerencias": [{{"titulo": ..., "descripcion": ..., '
                    f'"prioridad": ..., "plazo": ..., "impacto": ...}}]}}'
                ),
            }
        ],
    )

    text_blocks = [b for b in message.content if b.type == "text"]
    try:
        resultado = _parse_json_object(text_blocks[-1].text) if text_blocks else {}
    except (ValueError, json.JSONDecodeError):
        resultado = {"sugerencias": [{"titulo": text_blocks[-1].text if text_blocks else "Sin resultado"}]}

    entry = repo.crear(
        db,
        {
            "marca_id": marca_id,
            "tipo": "sugerencia",
            "contenido": resultado,
        },
    )
    db.commit()
    return entry


def listar_sugerencias(db: Session, marca_id: UUID) -> list[dict]:
    return repo.listar(db, marca_id, tipo="sugerencia")


def marcar_implementada(db: Session, marca_id: UUID, estrategia_id: UUID) -> dict:
    result = repo.marcar_implementada(db, estrategia_id, marca_id)
    if not result:
        raise AppError("Estrategia no encontrada", "NOT_FOUND", 404)
    db.commit()
    return result
