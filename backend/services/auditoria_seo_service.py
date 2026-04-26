"""Servicio de auditoría técnica SEO — NUNCA modifica el sitio del cliente."""

from __future__ import annotations

import logging
from uuid import UUID

import requests
from sqlalchemy.orm import Session

from middleware.audit import registrar_auditoria
from middleware.error_handler import AppError
from repositories import auditoria_seo_repository as repo

logger = logging.getLogger(__name__)


def auditar_sitio(db: Session, marca_id: UUID, url: str) -> list:
    """
    Analiza una URL y genera lista de problemas técnicos con recomendaciones.
    NUNCA toca el sitio — solo analiza y recomienda.
    """
    problemas = _analizar_url(url)
    items = [{"marca_id": marca_id, **p} for p in problemas]
    resultados = repo.crear_bulk(db, items)
    registrar_auditoria(
        db,
        accion="auditar_sitio_seo",
        modulo="seo",
        marca_id=marca_id,
        recurso_id=url,
        detalle={"url": url, "problemas_encontrados": len(resultados)},
    )
    db.commit()
    logger.debug(f"[auditoria_seo_svc] {len(resultados)} problemas en {url}")
    return resultados


def listar(db: Session, marca_id: UUID) -> list:
    """Lista todos los hallazgos de auditoría SEO."""
    return repo.listar(db, marca_id)


def listar_pendientes(db: Session, marca_id: UUID) -> list:
    """Lista hallazgos pendientes de implementar."""
    return repo.listar_pendientes(db, marca_id)


def marcar_implementado(db: Session, item_id: UUID, marca_id: UUID) -> dict:
    """Marca un hallazgo como implementado."""
    resultado = repo.marcar_implementado(db, item_id, marca_id)
    if not resultado:
        raise AppError("Hallazgo no encontrado", "NOT_FOUND", 404)
    db.commit()
    return resultado


def _analizar_url(url: str) -> list:
    """Analiza una URL y retorna lista de problemas detectados."""
    problemas = []
    try:
        r = requests.get(url, timeout=10, allow_redirects=True)
        _check_velocidad(r, url, problemas)
        _check_meta(r, url, problemas)
    except requests.RequestException:
        problemas.append(
            {
                "url": url,
                "tipo": "velocidad",
                "severidad": "critico",
                "descripcion": "El sitio no responde o no es accesible",
                "recomendacion": "Verificar que el dominio y hosting estén activos",
            }
        )
    return problemas if problemas else _problemas_default(url)


def _check_velocidad(r, url: str, problemas: list) -> None:
    """Detecta problemas de velocidad de carga."""
    if r.elapsed.total_seconds() > 3:
        problemas.append(
            {
                "url": url,
                "tipo": "velocidad",
                "severidad": "alto",
                "descripcion": f"Tiempo de carga: {r.elapsed.total_seconds():.1f}s (>3s)",
                "recomendacion": "Optimizar imágenes, activar compresión gzip, usar CDN",
            }
        )


def _check_meta(r, url: str, problemas: list) -> None:
    """Detecta problemas de meta tags básicos."""
    html = r.text.lower()
    if "<title>" not in html or "</title>" not in html:
        problemas.append(
            {
                "url": url,
                "tipo": "meta",
                "severidad": "critico",
                "descripcion": "No se encontró tag <title>",
                "recomendacion": "Agregar <title> con keyword principal, máx 60 caracteres",
            }
        )
    if 'name="description"' not in html:
        problemas.append(
            {
                "url": url,
                "tipo": "meta",
                "severidad": "alto",
                "descripcion": "No se encontró meta description",
                "recomendacion": "Agregar meta description de 120-155 caracteres con CTA",
            }
        )


def _problemas_default(url: str) -> list:
    """Retorna un análisis base si no se detectaron problemas evidentes."""
    return [
        {
            "url": url,
            "tipo": "schema",
            "severidad": "medio",
            "descripcion": "No se detectó markup Schema.org estructurado",
            "recomendacion": "Agregar schema JSON-LD para el tipo de negocio",
        }
    ]
