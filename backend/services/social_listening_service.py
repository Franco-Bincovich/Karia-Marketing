"""Servicio de Social Listening — monitorea todo, archiva todo siempre."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from integrations import mention_client
from middleware.audit import registrar_auditoria
from repositories import alertas_repository as alertas_repo
from repositories import config_listening_repository as config_repo
from repositories import menciones_repository as menciones_repo

logger = logging.getLogger(__name__)


def ejecutar_monitoreo(db: Session, marca_id: UUID) -> dict:
    """Obtiene menciones, guarda todo, detecta urgencia y competidores."""
    config = config_repo.obtener_o_crear(db, marca_id)
    todos_terminos = (config["terminos_marca"] or []) + (config["terminos_competidores"] or []) + (config["keywords_sector"] or [])
    if not todos_terminos:
        return {"menciones": 0, "urgentes": 0, "mensaje": "Sin términos configurados"}

    raw = mention_client.buscar_menciones(todos_terminos)
    umbral = config["umbral_urgencia"]
    marca_terms = set(config["terminos_marca"] or [])
    comp_terms = set(config["terminos_competidores"] or [])
    items = []
    urgentes = 0

    for m in raw:
        tipo = _clasificar_tipo(m["contenido"], marca_terms, comp_terms)
        es_urgente = m.get("alcance_estimado", 0) >= umbral
        sentimiento = mention_client.obtener_sentimiento(m["contenido"])
        items.append(
            {
                "marca_id": marca_id,
                "tipo": tipo,
                "fuente": m["fuente"],
                "url": m.get("url"),
                "autor": m.get("autor"),
                "contenido": m["contenido"],
                "sentimiento": sentimiento,
                "alcance_estimado": m.get("alcance_estimado", 0),
                "urgente": es_urgente,
            }
        )
        if es_urgente:
            urgentes += 1

    guardadas = menciones_repo.crear_bulk(db, items)

    for item in items:
        if item["urgente"]:
            alertas_repo.crear(
                db,
                {
                    "marca_id": marca_id,
                    "tipo": "mencion_urgente",
                    "mensaje": f"Mención urgente de {item['fuente']}: {item['contenido'][:80]}",
                    "datos": item,
                },
            )
        if item["tipo"] == "competidor":
            registrar_auditoria(
                db,
                accion="movimiento_competidor",
                modulo="listening",
                marca_id=marca_id,
                detalle={"fuente": item["fuente"], "contenido": item["contenido"][:100]},
            )

    db.commit()
    return {"menciones": len(guardadas), "urgentes": urgentes}


def analizar_sentimiento_marca(db: Session, marca_id: UUID) -> dict:
    """Calcula distribución de sentimiento de las últimas menciones."""
    menciones = menciones_repo.listar(db, marca_id)[:100]
    dist = {"positivo": 0, "negativo": 0, "neutro": 0, "mixto": 0}
    for m in menciones:
        s = m.get("sentimiento", "neutro")
        dist[s] = dist.get(s, 0) + 1
    total = len(menciones)
    return {
        "total": total,
        "distribucion": dist,
        "porcentajes": {k: round(v / total * 100, 1) if total else 0 for k, v in dist.items()},
    }


def detectar_crisis(db: Session, marca_id: UUID) -> bool:
    """Detecta crisis: negativas creciendo >50% en 24hs. Pausa autopilot si hay."""
    menciones = menciones_repo.listar(db, marca_id)
    ahora = datetime.now(timezone.utc)
    hace_24h = ahora - timedelta(hours=24)
    hace_48h = ahora - timedelta(hours=48)

    neg_24 = sum(1 for m in menciones if m["sentimiento"] == "negativo" and m["created_at"] and m["created_at"] > hace_24h.isoformat())
    neg_48 = sum(
        1 for m in menciones if m["sentimiento"] == "negativo" and m["created_at"] and hace_48h.isoformat() < m["created_at"] <= hace_24h.isoformat()
    )

    if neg_48 > 0 and neg_24 > neg_48 * 1.5:
        alertas_repo.crear(
            db,
            {
                "marca_id": marca_id,
                "tipo": "crisis_detectada",
                "canal": "panel",
                "mensaje": f"Crisis: menciones negativas +{int((neg_24 / neg_48 - 1) * 100)}% en 24hs ({neg_24} vs {neg_48})",
                "datos": {"neg_24h": neg_24, "neg_48h": neg_48},
            },
        )
        registrar_auditoria(
            db,
            accion="crisis_detectada",
            modulo="listening",
            marca_id=marca_id,
            detalle={"neg_24h": neg_24, "neg_48h": neg_48, "accion": "autopilot_pausado"},
        )
        db.commit()
        return True
    return False


def _clasificar_tipo(contenido: str, marca_terms: set, comp_terms: set) -> str:
    """Clasifica mención como marca, competidor o sector."""
    contenido_lower = contenido.lower()
    if any(t.lower() in contenido_lower for t in marca_terms):
        return "marca"
    if any(t.lower() in contenido_lower for t in comp_terms):
        return "competidor"
    return "sector"
