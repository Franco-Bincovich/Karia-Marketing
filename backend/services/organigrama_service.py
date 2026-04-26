"""Estructura jerárquica de la agencia NEXO — organigrama de agentes IA."""

from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy.orm import Session

from services import agentes_service as agentes_svc

logger = logging.getLogger(__name__)

AREAS = {
    "Dirección": {"color": "#FF6B00", "orden": 0},
    "Creativa": {"color": "#EC4899", "orden": 1},
    "Medios": {"color": "#3B82F6", "orden": 2},
    "Comunidad": {"color": "#10B981", "orden": 3},
    "Estrategia": {"color": "#8B5CF6", "orden": 4},
    "Datos": {"color": "#F59E0B", "orden": 5},
}

_ALL_AGENTS = ["contenido", "creativo", "social_media", "ads", "seo", "comunidad", "listening", "estrategia", "analytics", "reporting", "prospeccion"]

JERARQUIA = {
    "orquestador": {
        "area": "Dirección",
        "reporta_a": None,
        "supervisa": _ALL_AGENTS,
        "dependencias": [],
    },
    "contenido": {
        "area": "Creativa",
        "reporta_a": "orquestador",
        "supervisa": [],
        "dependencias": ["creativo"],
    },
    "creativo": {
        "area": "Creativa",
        "reporta_a": "orquestador",
        "supervisa": ["director_arte", "agente_visual", "copy_visual"],
        "dependencias": ["contenido"],
    },
    "director_arte": {
        "area": "Creativa",
        "reporta_a": "creativo",
        "supervisa": [],
        "dependencias": [],
    },
    "agente_visual": {
        "area": "Creativa",
        "reporta_a": "creativo",
        "supervisa": [],
        "dependencias": ["director_arte"],
    },
    "copy_visual": {
        "area": "Creativa",
        "reporta_a": "creativo",
        "supervisa": [],
        "dependencias": ["director_arte", "agente_visual"],
    },
    "social_media": {
        "area": "Medios",
        "reporta_a": "orquestador",
        "supervisa": [],
        "dependencias": ["contenido", "creativo"],
    },
    "ads": {
        "area": "Medios",
        "reporta_a": "orquestador",
        "supervisa": [],
        "dependencias": ["creativo", "analytics"],
    },
    "seo": {
        "area": "Medios",
        "reporta_a": "orquestador",
        "supervisa": [],
        "dependencias": ["contenido", "analytics"],
    },
    "comunidad": {
        "area": "Comunidad",
        "reporta_a": "orquestador",
        "supervisa": [],
        "dependencias": ["listening"],
    },
    "listening": {
        "area": "Comunidad",
        "reporta_a": "orquestador",
        "supervisa": [],
        "dependencias": [],
    },
    "estrategia": {
        "area": "Estrategia",
        "reporta_a": "orquestador",
        "supervisa": [],
        "dependencias": ["analytics", "listening"],
    },
    "analytics": {
        "area": "Datos",
        "reporta_a": "orquestador",
        "supervisa": [],
        "dependencias": [],
    },
    "reporting": {
        "area": "Datos",
        "reporta_a": "orquestador",
        "supervisa": [],
        "dependencias": ["analytics"],
    },
    "prospeccion": {
        "area": "Datos",
        "reporta_a": "orquestador",
        "supervisa": [],
        "dependencias": ["analytics"],
    },
}


# Colaboradores internos del Área Creativa (no son agentes configurables)
_COLABORADORES = {
    "director_arte": {"label": "Director de Arte", "icon": "🎬", "rol": "Analiza briefs y toma decisiones creativas"},
    "agente_visual": {"label": "Agente Visual", "icon": "🖼️", "rol": "Genera imágenes desde instrucciones del Director"},
    "copy_visual": {"label": "Copy Visual", "icon": "✏️", "rol": "Aplica texto y tipografía sobre imágenes"},
}


def obtener_organigrama(db: Session, marca_id: UUID, rol: str = "") -> dict:
    """Combina jerarquía estática con estado real de cada agente."""
    agentes_live = agentes_svc.obtener_config(db, marca_id, rol=rol)
    live_map = {a["nombre"]: a for a in agentes_live}

    nodos = {}
    for nombre, info in JERARQUIA.items():
        live = live_map.get(nombre, {})
        colab = _COLABORADORES.get(nombre, {})
        nodos[nombre] = {
            "nombre": nombre,
            "label": live.get("label") or colab.get("label") or nombre.replace("_", " ").title(),
            "icon": live.get("icon") or colab.get("icon", "⚙"),
            "rol": live.get("rol") or colab.get("rol", ""),
            "area": info["area"],
            "area_color": AREAS[info["area"]]["color"],
            "reporta_a": info["reporta_a"],
            "supervisa": info["supervisa"],
            "dependencias": info["dependencias"],
            "activo": live.get("activo", nombre in _COLABORADORES),
            "modo": live.get("modo", "copilot"),
            "estado": live.get("estado", "disponible" if nombre in _COLABORADORES else "bloqueado_v1"),
            "es_colaborador": nombre in _COLABORADORES,
        }

    return {"nodos": nodos, "areas": AREAS}
