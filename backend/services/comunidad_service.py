"""Servicio del Agente Comunidad — responde todo salvo criterios de escalado."""

from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy.orm import Session

from integrations.claude_client import _get_client
from middleware.audit import registrar_auditoria
from repositories import alertas_repository as alertas_repo
from repositories import config_comunidad_repository as config_repo
from repositories import contactos_repository
from repositories import mensajes_comunidad_repository as msg_repo

logger = logging.getLogger(__name__)

_COMMUNITY_MODEL = "claude-sonnet-4-20250514"

_CLASIFICACIONES_ESCALADO = {"agresivo", "spam"}


def procesar_mensaje(db: Session, marca_id: UUID, mensaje_data: dict) -> dict:
    """Clasifica, escala si necesario, genera respuesta o propone en copilot."""
    config = config_repo.obtener_o_crear(db, marca_id)
    mensaje_data["marca_id"] = marca_id
    msg = msg_repo.crear(db, mensaje_data)
    clasificacion = msg["clasificacion"]

    if _debe_escalar(clasificacion, config):
        motivo = f"Clasificación: {clasificacion}"
        msg_repo.marcar_escalado(db, UUID(msg["id"]), motivo)
        alertas_repo.crear(
            db,
            {
                "marca_id": marca_id,
                "tipo": "escalado_comunidad",
                "mensaje": f"Mensaje escalado: {motivo}",
                "datos": msg,
            },
        )
        registrar_auditoria(db, accion="escalar_mensaje", modulo="comunidad", marca_id=marca_id, recurso_id=msg["id"], detalle={"motivo": motivo})
        db.commit()
        return {**msg, "accion": "escalado"}

    if clasificacion == "lead":
        _crear_lead(db, marca_id, msg)

    if config["modo"] == "autopilot":
        respuesta = generar_respuesta(db, marca_id, msg["contenido"], clasificacion)
        resultado = msg_repo.marcar_respondido(db, UUID(msg["id"]), respuesta)
        db.commit()
        return {**resultado, "accion": "respondido_automaticamente"}

    respuesta = generar_respuesta(db, marca_id, msg["contenido"], clasificacion)
    db.commit()
    return {**msg, "respuesta_sugerida": respuesta, "accion": "pendiente_aprobacion"}


def generar_respuesta(db: Session, marca_id: UUID, contenido: str, clasificacion: str) -> str:
    """Genera respuesta con Claude usando el perfil de marca completo."""
    from repositories import memoria_marca_repository as memoria_repo

    memoria_text = memoria_repo.obtener_para_agente(db, marca_id)

    system = (
        "Sos el Agente Comunidad de Nexo Marketing. Respondés en nombre de la marca.\n"
        "Nunca inventás información del negocio que no tenés.\n"
        "Si no sabés algo, decís que vas a consultar y derivás.\n"
        "Ante comentarios negativos: reconocés el malestar, mostrás disposición a resolver, "
        "invitás a continuar en privado.\n"
        "Respondé SOLO con el texto de la respuesta, sin explicaciones.\n\n"
        f"PERFIL DE MARCA:\n{memoria_text}"
    )
    try:
        message = _get_client().messages.create(
            model=_COMMUNITY_MODEL,
            max_tokens=512,
            system=system,
            messages=[{"role": "user", "content": f"[{clasificacion}] {contenido}"}],
        )
        blocks = [b for b in message.content if b.type == "text"]
        return blocks[-1].text if blocks else "Gracias por tu mensaje, lo revisamos pronto."
    except Exception as exc:
        logger.warning(f"[comunidad_svc] Claude falló: {exc}")
        return "Gracias por tu mensaje. Lo revisamos y te respondemos a la brevedad."


def listar_pendientes(db: Session, marca_id: UUID) -> list:
    """Lista mensajes pendientes de respuesta."""
    return msg_repo.listar_pendientes(db, marca_id)


def listar_leads_detectados(db: Session, marca_id: UUID) -> list:
    """Lista leads detectados en DMs."""
    return msg_repo.listar_leads(db, marca_id)


def listar_historial(db: Session, marca_id: UUID) -> list:
    """Historial de mensajes gestionados (respondidos e ignorados)."""
    return msg_repo.listar_respondidos(db, marca_id)


def _debe_escalar(clasificacion: str, config: dict) -> bool:
    """Determina si un mensaje debe escalarse."""
    if clasificacion == "agresivo" and not config["responder_agresivos"]:
        return True
    if clasificacion == "spam" and not config["responder_spam"]:
        return True
    criterios = config.get("criterios_escalado") or []
    return clasificacion in criterios


def _crear_lead(db: Session, marca_id: UUID, msg: dict) -> None:
    """Crea un contacto en contactos_mkt a partir de un lead detectado en DM."""
    contactos_repository.crear(
        db,
        {
            "marca_id": marca_id,
            "cliente_id": marca_id,
            "nombre": msg.get("autor_username", "Lead DM"),
            "empresa": "Desconocida",
            "origen": "comunidad",
            "notas": f"Lead detectado en {msg['red_social']}: {msg['contenido'][:100]}",
        },
    )
