"""
Servicio de monitoreo post-publicación — Agente Social Media.

Revisa métricas de las primeras 2hs y alerta si el engagement es bajo
comparado con el promedio histórico de la marca. Los alertas quedan
registrados en auditoria_mkt para trazabilidad.
"""

import logging
from uuid import UUID

from sqlalchemy.orm import Session

from integrations import linkedin_client, meta_client
from middleware.audit import registrar_auditoria
from middleware.error_handler import AppError
from repositories import cuentas_sociales_repository as cuentas_repo
from repositories import publicaciones_repository as pub_repo

logger = logging.getLogger(__name__)

# Umbral: si engagement actual < FACTOR * promedio histórico → engagement_bajo
UMBRAL_ENGAGEMENT = 0.5


def monitorear_publicacion(db: Session, publicacion_id: UUID, marca_id: UUID) -> dict:
    """
    Obtiene métricas de las primeras 2hs de una publicación y evalúa el engagement.

    Flujo:
      1. Obtiene la publicación de la BD
      2. Busca la cuenta social de la marca para esa red
      3. Llama a la API correspondiente para obtener métricas reales
      4. Calcula si el engagement es bajo vs el promedio histórico de la marca
      5. Actualiza publicaciones_mkt con métricas y flag engagement_bajo
      6. Si engagement_bajo=True registra alerta en auditoria_mkt

    Returns:
        Dict de la publicación con métricas actualizadas

    Raises:
        AppError 404 si la publicación no existe
    """
    rows = pub_repo.listar(db, marca_id)
    pub = next((r for r in rows if r["id"] == str(publicacion_id)), None)
    if not pub:
        raise AppError("Publicación no encontrada", "NOT_FOUND", 404)

    if pub["estado"] != "publicado" or not pub["post_id_externo"]:
        logger.debug(f"[monitoring] publicacion {publicacion_id} no lista para monitoreo")
        return pub

    cuenta = cuentas_repo.obtener_por_red(db, marca_id, pub["red_social"])
    access_token = "mock"
    if cuenta and cuenta.access_token_encrypted:
        from utils.security import decrypt_token
        access_token = decrypt_token(cuenta.access_token_encrypted)

    metricas_raw = _obtener_metricas(pub["red_social"], access_token, pub["post_id_externo"])

    promedio = pub_repo.promedio_engagement(db, marca_id)
    engagement_actual = metricas_raw["likes"] + metricas_raw["comentarios"]
    es_bajo = promedio > 0 and engagement_actual < UMBRAL_ENGAGEMENT * promedio

    metricas = {
        "likes": metricas_raw["likes"],
        "comentarios": metricas_raw["comentarios"],
        "alcance": metricas_raw["alcance"],
        "engagement_bajo": es_bajo,
    }

    resultado = pub_repo.actualizar_metricas(db, publicacion_id, metricas)

    if es_bajo:
        logger.warning(f"[monitoring] engagement bajo — pub={publicacion_id}, actual={engagement_actual}, avg={promedio:.1f}")
        registrar_auditoria(
            db,
            accion="engagement_bajo",
            modulo="social_media",
            marca_id=marca_id,
            recurso_id=str(publicacion_id),
            detalle={
                "red_social": pub["red_social"],
                "likes": metricas_raw["likes"],
                "comentarios": metricas_raw["comentarios"],
                "promedio_historico": promedio,
            },
        )

    db.commit()
    return resultado


def _obtener_metricas(red_social: str, access_token: str, post_id: str) -> dict:
    """Despacha la llamada de métricas al cliente correcto."""
    if red_social in ("instagram", "facebook"):
        return meta_client.obtener_metricas_post(access_token, post_id)
    if red_social == "linkedin":
        return linkedin_client.obtener_metricas_post(access_token, post_id)
    return {"likes": 0, "comentarios": 0, "alcance": 0, "mock": True}
