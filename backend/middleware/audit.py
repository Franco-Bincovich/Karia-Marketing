"""Middleware y utilidad para registrar acciones en auditoria_mkt."""

from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from models.permisos_models import AuditoriaMkt


ACCIONES_SENSIBLES = {
    "login", "logout", "crear_usuario", "eliminar_usuario",
    "cambiar_permisos", "crear_cliente", "crear_marca",
    "actualizar_feature_flag",
}


def registrar_auditoria(
    db: Session,
    accion: str,
    modulo: str,
    usuario_id: Optional[UUID] = None,
    cliente_id: Optional[UUID] = None,
    marca_id: Optional[UUID] = None,
    recurso_id: Optional[str] = None,
    detalle: Optional[Dict[str, Any]] = None,
    ip: Optional[str] = None,
) -> None:
    """Registra una entrada en auditoria_mkt sin hacer commit (el caller lo hace)."""
    entrada = AuditoriaMkt(
        usuario_id=usuario_id,
        cliente_id=cliente_id,
        marca_id=marca_id,
        accion=accion,
        modulo=modulo,
        recurso_id=recurso_id,
        detalle=detalle,
        ip=ip,
    )
    db.add(entrada)


def get_client_ip(request_scope: dict) -> Optional[str]:
    """Extrae IP del cliente del scope ASGI."""
    client = request_scope.get("client")
    if client:
        return client[0]
    headers = dict(request_scope.get("headers", []))
    forwarded = headers.get(b"x-forwarded-for", b"").decode()
    return forwarded.split(",")[0].strip() if forwarded else None
