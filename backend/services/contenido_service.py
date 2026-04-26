"""
Servicio de generación de contenido IA — Módulo 5.

Genera 3 variantes A/B/C con perfil de marca como contexto.
Soporta Copilot (aprobación manual) y Autopilot (publicación directa).
Límite de 30 posts/mes para Basic; Premium y superadmin sin límite.
"""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from integrations import claude_client
from middleware.error_handler import AppError
from repositories import aprendizaje_repository as ap_repo
from repositories import contenido_repository as repo
from repositories import memoria_marca_repository as memoria_repo
from repositories import templates_repository as tpl_repo
from utils.security import decrypt_token

logger = logging.getLogger(__name__)

BASIC_LIMIT = 30


def _get_context(db: Session, marca_id: UUID) -> tuple:
    """Obtiene plan, rol-equivalente info, y memoria de marca."""
    from models.cliente_models import ClienteMkt, MarcaMkt

    marca = db.query(MarcaMkt).filter(MarcaMkt.id == marca_id).first()
    if not marca:
        raise AppError("Marca no encontrada", "MARCA_NOT_FOUND", 404)
    cliente = db.query(ClienteMkt).filter(ClienteMkt.id == marca.cliente_id).first()
    if not cliente:
        raise AppError("Cliente no encontrado", "CLIENT_NOT_FOUND", 404)
    memoria_text = memoria_repo.obtener_para_agente(db, marca_id)
    return cliente, memoria_text


def _check_limit(db: Session, marca_id: UUID, plan: str, rol: str):
    """Valida límite de 30/mes para Basic. Premium y superadmin sin límite."""
    if plan == "Premium" or rol == "superadmin":
        return
    count = repo.contar_mes_actual(db, marca_id)
    if count >= BASIC_LIMIT:
        raise AppError(
            f"Alcanzaste el límite de {BASIC_LIMIT} contenidos/mes del plan Basic. Upgrade a Premium.",
            "PLAN_LIMIT_CONTENT",
            403,
        )


def _get_custom_api_key(cliente) -> Optional[str]:
    """Devuelve la API key propia desencriptada si existe."""
    if cliente.anthropic_api_key_encrypted:
        return decrypt_token(cliente.anthropic_api_key_encrypted)
    return None


def generar_contenido(
    db: Session,
    marca_id: UUID,
    cliente_id: UUID,
    red_social: str,
    formato: str,
    objetivo: str,
    tono: str,
    tema: str,
    modo: str = "copilot",
    rol: str = "",
) -> dict:
    """Genera 3 variantes A/B/C con el perfil de marca como contexto."""
    cliente, memoria_text = _get_context(db, marca_id)
    _check_limit(db, marca_id, cliente.plan, rol)

    prefs = ap_repo.obtener_preferencias(db, marca_id)
    if prefs["tono_preferido"] and not tono:
        tono = prefs["tono_preferido"]

    custom_key = _get_custom_api_key(cliente) if cliente.plan == "Premium" else None

    resultado = claude_client.generar_contenido_ia(
        red_social=red_social,
        formato=formato,
        objetivo=objetivo,
        tono=tono,
        tema=tema,
        memoria_marca=memoria_text,
        custom_api_key=custom_key,
    )

    estado = "aprobado" if modo == "autopilot" else "pendiente_aprobacion"
    data = {
        "marca_id": marca_id,
        "cliente_id": cliente_id,
        "red_social": red_social,
        "formato": formato,
        "objetivo": objetivo,
        "tono": tono,
        "tema": tema,
        "copy_a": resultado["copy_a"],
        "copy_b": resultado["copy_b"],
        "copy_c": resultado.get("copy_c"),
        "hashtags_a": resultado.get("hashtags_a"),
        "hashtags_b": resultado.get("hashtags_b"),
        "hashtags_c": resultado.get("hashtags_c"),
        "cta_a": resultado.get("cta_a"),
        "cta_b": resultado.get("cta_b"),
        "cta_c": resultado.get("cta_c"),
        "estado": estado,
        "modo": modo,
    }
    contenido = repo.crear(db, data)

    repo.guardar_version(
        db,
        UUID(contenido["id"]),
        {
            "copy_a": resultado["copy_a"],
            "copy_b": resultado["copy_b"],
            "copy_c": resultado.get("copy_c"),
            "creado_por": "ia",
        },
    )

    db.commit()
    contenido["variable_testeada"] = resultado.get("variable_testeada")
    return contenido


def publicar_directo(
    db: Session,
    marca_id: UUID,
    contenido_id: UUID,
    variante: str,
    rol: str = "",
) -> dict:
    """Aprueba y publica inmediatamente vía Zernio. Solo Premium y superadmin."""
    cliente, _ = _get_context(db, marca_id)
    if cliente.plan != "Premium" and rol != "superadmin":
        raise AppError(
            "Publicación directa solo disponible en Premium",
            "PLAN_LIMIT",
            403,
        )

    if variante not in ("a", "b", "c"):
        raise AppError("La variante debe ser 'a', 'b' o 'c'", "INVALID_VARIANTE", 400)

    obj = repo.obtener(db, contenido_id, marca_id)
    if not obj:
        raise AppError("Contenido no encontrado", "NOT_FOUND", 404)

    copy_field = f"copy_{variante}"
    copy_text = getattr(obj, copy_field)
    if not copy_text:
        raise AppError(f"Variante {variante} sin contenido", "EMPTY_VARIANTE", 400)

    repo.actualizar_campos(
        db,
        obj,
        {
            "estado": "publicado",
            "variante_seleccionada": variante,
            "modo": "autopilot",
        },
    )

    ap_repo.registrar(
        db,
        {
            "marca_id": marca_id,
            "contenido_id": contenido_id,
            "tipo": "aprobacion",
            "red_social": obj.red_social,
            "formato": obj.formato,
            "tono": obj.tono,
            "copy_final": copy_text,
        },
    )
    db.commit()

    from services import zernio_service

    try:
        pub = zernio_service.publicar_ahora(
            db,
            marca_id,
            obj.red_social,
            copy_text,
            imagen_url=obj.imagen_url,
            formato=obj.formato or "post",
        )
        return {"contenido": repo._s(obj), "publicacion": pub}
    except AppError:
        repo.actualizar_campos(db, obj, {"estado": "aprobado"})
        db.commit()
        raise


def guardar_api_key(db: Session, cliente_id: UUID, api_key: str) -> dict:
    """Guarda la API key propia de Anthropic encriptada."""
    from models.cliente_models import ClienteMkt
    from utils.security import encrypt_token

    cliente = db.query(ClienteMkt).filter(ClienteMkt.id == cliente_id).first()
    if not cliente:
        raise AppError("Cliente no encontrado", "CLIENT_NOT_FOUND", 404)
    if cliente.plan != "Premium":
        raise AppError("Solo Premium puede usar API key propia", "PLAN_LIMIT", 403)
    cliente.anthropic_api_key_encrypted = encrypt_token(api_key)
    db.commit()
    return {"message": "API key guardada correctamente", "has_custom_key": True}


def get_usage_info(db: Session, marca_id: UUID, rol: str = "") -> dict:
    """Retorna info de uso del mes para el cliente."""
    cliente, _ = _get_context(db, marca_id)
    count = repo.contar_mes_actual(db, marca_id)
    has_limit = cliente.plan != "Premium" and rol != "superadmin"
    return {
        "posts_mes": count,
        "limite": BASIC_LIMIT if has_limit else None,
        "has_custom_key": bool(cliente.anthropic_api_key_encrypted),
        "plan": cliente.plan,
        "autopilot_enabled": cliente.plan == "Premium" or rol == "superadmin",
    }


def listar(db: Session, marca_id: UUID, estado: Optional[str] = None) -> list[dict]:
    """Retorna contenido con filtro opcional de estado."""
    return repo.listar(db, marca_id, estado=estado)


def obtener_versiones(db: Session, contenido_id: UUID, marca_id: UUID) -> list[dict]:
    if not repo.obtener(db, contenido_id, marca_id):
        raise AppError("Contenido no encontrado", "NOT_FOUND", 404)
    return repo.listar_versiones(db, contenido_id)


def crear_template(db: Session, marca_id: UUID, template_data: dict) -> dict:
    data = {**template_data, "marca_id": marca_id}
    resultado = tpl_repo.crear(db, data)
    db.commit()
    return resultado


def listar_templates(db: Session, marca_id: UUID) -> list[dict]:
    return tpl_repo.listar(db, marca_id)


def eliminar_template(db: Session, template_id: UUID, marca_id: UUID) -> bool:
    eliminado = tpl_repo.eliminar(db, template_id, marca_id)
    if not eliminado:
        raise AppError("Template no encontrado", "NOT_FOUND", 404)
    db.commit()
    return True
