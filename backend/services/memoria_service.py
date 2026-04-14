"""Servicio de Memoria de Marca — formatea memoria según el agente."""
from __future__ import annotations

import json
import logging
from uuid import UUID

from sqlalchemy.orm import Session

from repositories import memoria_marca_repository as memoria_repo

logger = logging.getLogger(__name__)

_CAMPOS_POR_AGENTE = {
    "contenido": ["nombre_marca", "tono_voz", "palabras_clave", "palabras_prohibidas",
                   "ejemplos_contenido_aprobado", "productos_servicios", "publico_objetivo"],
    "comunidad": ["nombre_marca", "tono_voz", "preguntas_frecuentes",
                   "politica_respuestas", "productos_servicios", "palabras_prohibidas"],
    "ads": ["nombre_marca", "productos_servicios", "icp_descripcion", "icp_cargo",
            "icp_industria", "diferenciadores", "objetivos_periodo"],
    "seo": ["nombre_marca", "palabras_clave", "productos_servicios",
            "competidores", "sitio_web", "industria"],
    "social_media": ["nombre_marca", "tono_voz", "palabras_prohibidas",
                      "ejemplos_contenido_aprobado", "colores_marca"],
    "prospeccion": ["nombre_marca", "icp_descripcion", "icp_cargo", "icp_industria",
                    "icp_tamano_empresa", "productos_servicios", "diferenciadores"],
}


def obtener_para_agente(db: Session, marca_id: UUID, agente: str) -> str:
    """Retorna la memoria formateada según el agente que la solicita."""
    memoria = memoria_repo.obtener_o_crear(db, marca_id)
    campos = _CAMPOS_POR_AGENTE.get(agente, list(_CAMPOS_POR_AGENTE.get("contenido", [])))
    partes = []
    for campo in campos:
        valor = memoria.get(campo)
        if not valor:
            continue
        label = campo.replace("_", " ").capitalize()
        if isinstance(valor, (dict, list)):
            partes.append(f"{label}: {json.dumps(valor, ensure_ascii=False)}")
        elif isinstance(valor, list):
            partes.append(f"{label}: {', '.join(str(v) for v in valor)}")
        else:
            partes.append(f"{label}: {valor}")
    return ". ".join(partes) if partes else ""


def actualizar_desde_aprendizaje(db: Session, marca_id: UUID, tipo: str,
                                  datos: dict) -> dict:
    """Actualiza memoria de marca basándose en feedback del motor de aprendizaje."""
    memoria = memoria_repo.obtener_o_crear(db, marca_id)
    actualizacion = {}

    if tipo == "tono_rechazado":
        prohibidas = list(memoria.get("palabras_prohibidas") or [])
        nueva = datos.get("palabra")
        if nueva and nueva not in prohibidas:
            prohibidas.append(nueva)
            actualizacion["palabras_prohibidas"] = prohibidas

    elif tipo == "tono_preferido":
        clave = list(memoria.get("palabras_clave") or [])
        nueva = datos.get("palabra")
        if nueva and nueva not in clave:
            clave.append(nueva)
            actualizacion["palabras_clave"] = clave

    elif tipo == "ejemplo_aprobado":
        ejemplos = list(memoria.get("ejemplos_contenido_aprobado") or [])
        nuevo = datos.get("ejemplo")
        if nuevo and nuevo not in ejemplos:
            ejemplos.append(nuevo)
            actualizacion["ejemplos_contenido_aprobado"] = ejemplos[:20]

    elif tipo == "tono_voz":
        tono = datos.get("tono")
        if tono:
            actualizacion["tono_voz"] = tono

    if actualizacion:
        resultado = memoria_repo.actualizar(db, marca_id, actualizacion)
        db.commit()
        logger.debug(f"[memoria_svc] actualizada desde aprendizaje — tipo={tipo}")
        return resultado
    return memoria
