"""Servicio de Social Listening — M09. Busca menciones via Zernio o Claude web search."""

import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from middleware.error_handler import AppError
from repositories import alertas_repository as alertas_repo
from repositories import config_listening_repository as config_repo
from repositories import memoria_marca_repository as memoria_repo
from repositories import menciones_repository as menciones_repo

logger = logging.getLogger(__name__)


def buscar_menciones(db: Session, marca_id: UUID) -> dict:
    """Busca menciones nuevas del nombre de marca usando Claude web search."""
    config = config_repo.obtener_o_crear(db, marca_id)
    memoria = memoria_repo.obtener_o_crear(db, marca_id)
    nombre_marca = memoria.get("nombre_marca")

    if not nombre_marca or not nombre_marca.strip():
        return {
            "menciones": 0,
            "mensaje": "Completá el onboarding para activar el Social Listening. Se necesita el nombre de la marca.",
        }

    terminos = config.get("terminos_marca") or []
    if nombre_marca not in terminos:
        terminos = [nombre_marca] + terminos

    descripcion = memoria.get("descripcion") or ""
    industria = memoria.get("industria") or ""

    from integrations.claude_client import _SEARCH_MODEL, _WEB_SEARCH_TOOL, _get_client, _parse_json_object

    context_parts = [f"'{nombre_marca}'"]
    if descripcion:
        context_parts.append(f"(empresa/marca: {descripcion[:100]})")
    if industria:
        context_parts.append(f"del sector {industria}")

    client = _get_client()
    message = client.messages.create(
        model=_SEARCH_MODEL,
        max_tokens=2048,
        tools=_WEB_SEARCH_TOOL,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Buscá menciones recientes de la marca {' '.join(context_parts)} en redes sociales y web.\n"
                    f"Términos de búsqueda adicionales: {', '.join(terminos)}\n\n"
                    f"IMPORTANTE: Solo incluí menciones que se refieran a esta marca/empresa/negocio específico. "
                    f"Ignorá resultados de personas homónimas o temas no relacionados.\n\n"
                    f"Para cada mención encontrá:\n"
                    f"- plataforma (instagram, facebook, twitter, linkedin, web, foro)\n"
                    f"- usuario o autor\n"
                    f"- texto de la mención\n"
                    f"- sentimiento (positivo, neutro, negativo)\n"
                    f"- score_sentimiento (0 = muy negativo, 50 = neutro, 100 = muy positivo)\n"
                    f"- url si la encontrás\n\n"
                    f"Si no encontrás menciones reales de esta marca, retorná un array vacío.\n"
                    f'Respondé SOLO con JSON: {{"menciones": [{{"plataforma": ..., "usuario": ..., '
                    f'"texto": ..., "sentimiento": ..., "score_sentimiento": ..., "url": ...}}]}}'
                ),
            }
        ],
    )

    text_blocks = [b for b in message.content if b.type == "text"]
    if not text_blocks:
        return {"menciones": 0, "mensaje": "Sin resultados"}

    try:
        resultado = _parse_json_object(text_blocks[-1].text)
        raw_menciones = resultado.get("menciones", [])
    except (ValueError, json.JSONDecodeError):
        return {"menciones": 0, "mensaje": "Error procesando resultados"}

    items = []
    for m in raw_menciones:
        sent = m.get("sentimiento", "neutro")
        score = m.get("score_sentimiento", 50)
        es_urgente = sent == "negativo" and score < 20

        items.append(
            {
                "marca_id": marca_id,
                "tipo": "marca",
                "fuente": m.get("plataforma", "web"),
                "url": m.get("url"),
                "autor": m.get("usuario"),
                "contenido": m.get("texto", ""),
                "sentimiento": sent,
                "score_sentimiento": score,
                "alcance_estimado": 0,
                "urgente": es_urgente,
                "alerta_generada": es_urgente,
            }
        )

    guardadas = menciones_repo.crear_bulk(db, items)

    # Generate alerts for urgent mentions
    urgentes = sum(1 for i in items if i["urgente"])
    for item in items:
        if item["urgente"]:
            alertas_repo.crear(
                db,
                {
                    "marca_id": marca_id,
                    "tipo": "mencion_negativa",
                    "mensaje": f"Mención negativa en {item['fuente']}: {item['contenido'][:80]}",
                    "datos": item,
                },
            )

    # Check for crisis
    crisis = _detectar_crisis(db, marca_id)

    db.commit()
    return {
        "menciones": len(guardadas),
        "urgentes": urgentes,
        "crisis": crisis,
    }


def obtener_resumen(db: Session, marca_id: UUID) -> dict:
    """Resumen estadístico del listening."""
    total = menciones_repo.total_menciones(db, marca_id)
    por_sent = menciones_repo.contar_por_sentimiento(db, marca_id)

    positivos = por_sent.get("positivo", 0)
    negativos = por_sent.get("negativo", 0)
    neutros = por_sent.get("neutro", 0)
    mixtos = por_sent.get("mixto", 0)

    return {
        "total": total,
        "positivos": positivos,
        "negativos": negativos,
        "neutros": neutros,
        "mixtos": mixtos,
        "porcentajes": {
            "positivo": round(positivos / total * 100, 1) if total else 0,
            "negativo": round(negativos / total * 100, 1) if total else 0,
            "neutro": round(neutros / total * 100, 1) if total else 0,
            "mixto": round(mixtos / total * 100, 1) if total else 0,
        },
        "tendencia": "estable",
    }


def listar_menciones(
    db: Session,
    marca_id: UUID,
    sentimiento: Optional[str] = None,
    plataforma: Optional[str] = None,
    desde: Optional[str] = None,
) -> list[dict]:
    """Lista menciones con filtros."""
    desde_dt = None
    if desde:
        try:
            import re

            clean = re.sub(r"\.\d+", "", desde).replace("Z", "+00:00")
            desde_dt = datetime.fromisoformat(clean)
        except (ValueError, TypeError):
            pass
    return menciones_repo.listar_filtrado(db, marca_id, sentimiento=sentimiento, plataforma=plataforma, desde=desde_dt)


def listar_alertas(db: Session, marca_id: UUID) -> list[dict]:
    """Lista alertas activas de listening."""
    return alertas_repo.listar_por_tipo(db, marca_id, "mencion_negativa") + alertas_repo.listar_por_tipo(db, marca_id, "crisis_detectada")


def marcar_procesada(db: Session, mencion_id: UUID) -> dict:
    """Marca una mención como procesada."""
    result = menciones_repo.marcar_procesado(db, mencion_id)
    if not result:
        raise AppError("Mención no encontrada", "NOT_FOUND", 404)
    db.commit()
    return result


def _detectar_crisis(db: Session, marca_id: UUID) -> bool:
    """Detecta crisis: pico de negativas en 24h."""
    menciones = menciones_repo.listar(db, marca_id)
    ahora = datetime.now(timezone.utc)
    hace_24h = ahora - timedelta(hours=24)
    hace_48h = ahora - timedelta(hours=48)

    neg_24 = sum(1 for m in menciones if m["sentimiento"] == "negativo" and m.get("created_at") and m["created_at"] > hace_24h.isoformat())
    neg_48 = sum(
        1
        for m in menciones
        if m["sentimiento"] == "negativo" and m.get("created_at") and hace_48h.isoformat() < m["created_at"] <= hace_24h.isoformat()
    )

    if neg_48 > 0 and neg_24 > neg_48 * 1.5:
        alertas_repo.crear(
            db,
            {
                "marca_id": marca_id,
                "tipo": "crisis_detectada",
                "mensaje": f"Crisis: negativas +{int((neg_24 / neg_48 - 1) * 100)}% en 24hs ({neg_24} vs {neg_48})",
                "datos": {"neg_24h": neg_24, "neg_48h": neg_48},
            },
        )
        return True
    return False
