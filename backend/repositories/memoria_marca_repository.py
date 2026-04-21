"""Repositorio para memoria_marca_mkt."""
from __future__ import annotations

import json
import logging
from uuid import UUID

from sqlalchemy.orm import Session

from models.onboarding_models import MemoriaMarcaMkt

logger = logging.getLogger(__name__)

_CAMPOS_MINIMOS = {"nombre_marca", "industria", "descripcion", "tono_voz"}


def _s(m: MemoriaMarcaMkt) -> dict:
    """Serializa un MemoriaMarcaMkt a dict."""
    return {
        "id": str(m.id), "marca_id": str(m.marca_id),
        "nombre_marca": m.nombre_marca, "industria": m.industria,
        "descripcion": m.descripcion, "propuesta_valor": m.propuesta_valor,
        "productos_servicios": m.productos_servicios,
        "publico_objetivo": m.publico_objetivo, "tono_voz": m.tono_voz,
        "palabras_clave": m.palabras_clave or [],
        "palabras_prohibidas": m.palabras_prohibidas or [],
        "colores_marca": m.colores_marca or [], "tipografia": m.tipografia,
        "ejemplos_contenido_aprobado": m.ejemplos_contenido_aprobado or [],
        "competidores": m.competidores, "diferenciadores": m.diferenciadores or [],
        "sitio_web": m.sitio_web, "preguntas_frecuentes": m.preguntas_frecuentes,
        "politica_respuestas": m.politica_respuestas,
        "icp_descripcion": m.icp_descripcion, "icp_cargo": m.icp_cargo or [],
        "icp_industria": m.icp_industria or [],
        "icp_tamano_empresa": m.icp_tamano_empresa,
        "objetivos_periodo": m.objetivos_periodo,
        # Campos expandidos (migration 035)
        "ciudad_zona": m.ciudad_zona,
        "dolor_cliente": m.dolor_cliente,
        "cta_principal": m.cta_principal,
        "frecuencia_publicacion": m.frecuencia_publicacion,
        "aprobacion_contenido": m.aprobacion_contenido,
        "redes_activas": m.redes_activas or [],
        "adjetivos_marca": m.adjetivos_marca or [],
        "ventaja_competitiva": m.ventaja_competitiva,
        "testimonios_resultados": m.testimonios_resultados,
        "temporada_alta_baja": m.temporada_alta_baja,
        "fechas_especiales": m.fechas_especiales,
        "tiene_fotos_propias": m.tiene_fotos_propias,
        "preferencia_imagenes": m.preferencia_imagenes,
        "personalidad_marca": m.personalidad_marca,
        "marcas_referencia": m.marcas_referencia,
        "estetica_visual": m.estetica_visual,
        "updated_at": m.updated_at.isoformat() if m.updated_at else None,
    }


def obtener_o_crear(db: Session, marca_id: UUID) -> dict:
    """Devuelve la memoria de marca, creando un registro vacío si no existe."""
    obj = db.query(MemoriaMarcaMkt).filter(MemoriaMarcaMkt.marca_id == marca_id).first()
    if not obj:
        obj = MemoriaMarcaMkt(marca_id=marca_id)
        db.add(obj)
        db.flush()
        logger.debug(f"[memoria_repo] creada vacía — marca={marca_id}")
    return _s(obj)


def actualizar(db: Session, marca_id: UUID, datos: dict) -> dict:
    """Actualiza campos de la memoria de marca."""
    obj = db.query(MemoriaMarcaMkt).filter(MemoriaMarcaMkt.marca_id == marca_id).first()
    if not obj:
        obj = MemoriaMarcaMkt(marca_id=marca_id)
        db.add(obj)
    for k, v in datos.items():
        if hasattr(obj, k) and k not in ("id", "marca_id"):
            setattr(obj, k, v)
    db.flush()
    return _s(obj)


def obtener_para_agente(db: Session, marca_id: UUID) -> str:
    """Retorna la memoria formateada como texto para system prompts."""
    obj = db.query(MemoriaMarcaMkt).filter(MemoriaMarcaMkt.marca_id == marca_id).first()
    if not obj:
        return ""
    partes = []
    if obj.nombre_marca:
        partes.append(f"Marca: {obj.nombre_marca}")
    if obj.industria:
        partes.append(f"Industria: {obj.industria}")
    if obj.descripcion:
        partes.append(f"Descripción: {obj.descripcion}")
    if obj.propuesta_valor:
        partes.append(f"Propuesta de valor: {obj.propuesta_valor}")
    if obj.tono_voz:
        partes.append(f"Tono: {obj.tono_voz}")
    if obj.publico_objetivo:
        partes.append(f"Público objetivo: {obj.publico_objetivo}")
    if obj.palabras_clave:
        partes.append(f"Palabras clave: {', '.join(obj.palabras_clave)}")
    if obj.palabras_prohibidas:
        partes.append(f"Palabras prohibidas: {', '.join(obj.palabras_prohibidas)}")
    if obj.productos_servicios:
        partes.append(f"Productos: {json.dumps(obj.productos_servicios, ensure_ascii=False)}")
    if obj.diferenciadores:
        partes.append(f"Diferenciadores: {', '.join(obj.diferenciadores)}")
    if obj.sitio_web:
        partes.append(f"Sitio web: {obj.sitio_web}")
    if obj.ciudad_zona:
        partes.append(f"Ubicación: {obj.ciudad_zona}")
    if obj.dolor_cliente:
        partes.append(f"Dolor del cliente: {obj.dolor_cliente}")
    if obj.cta_principal:
        partes.append(f"CTA principal: {obj.cta_principal}")
    if obj.frecuencia_publicacion:
        partes.append(f"Frecuencia: {obj.frecuencia_publicacion}")
    if obj.redes_activas:
        partes.append(f"Redes activas: {', '.join(obj.redes_activas)}")
    if obj.estetica_visual:
        partes.append(f"Estética visual: {obj.estetica_visual}")
    if obj.personalidad_marca:
        partes.append(f"Personalidad: {obj.personalidad_marca}")
    return ". ".join(partes)


def esta_completa(db: Session, marca_id: UUID) -> bool:
    """Retorna True si los campos mínimos de la memoria están completos."""
    obj = db.query(MemoriaMarcaMkt).filter(MemoriaMarcaMkt.marca_id == marca_id).first()
    if not obj:
        return False
    return all(getattr(obj, campo, None) for campo in _CAMPOS_MINIMOS)
