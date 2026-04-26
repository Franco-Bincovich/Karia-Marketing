"""Adaptador HTTP para el módulo de Contenido IA."""

import logging
from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.orm import Session

from middleware.error_handler import AppError
from services import contenido_feedback_service as feedback_svc
from services import contenido_service as svc

logger = logging.getLogger(__name__)


class GenerarRequest(BaseModel):
    red_social: str
    formato: str
    objetivo: str
    tono: str
    tema: str
    modo: str = "copilot"


class AprobarRequest(BaseModel):
    variante: str


class RechazarRequest(BaseModel):
    comentario: str


class EditarRequest(BaseModel):
    copy_editado: str
    variante: str


class PublicarDirectoRequest(BaseModel):
    variante: str


class GuardarApiKeyRequest(BaseModel):
    api_key: str


class TemplateRequest(BaseModel):
    nombre: str
    red_social: str
    formato: str
    copy_text: str
    hashtags: Optional[str] = None
    tono: Optional[str] = None
    objetivo: Optional[str] = None


def _marca(x_marca_id: Optional[str]) -> UUID:
    if not x_marca_id:
        raise AppError("Header X-Marca-ID es requerido", "MISSING_MARCA_ID", 400)
    try:
        return UUID(x_marca_id)
    except ValueError:
        raise AppError("X-Marca-ID debe ser un UUID válido", "INVALID_MARCA_ID", 400)


class ContenidoController:
    def __init__(self, db: Session):
        self.db = db

    def generar(self, body: GenerarRequest, x_marca_id: Optional[str], current_user: dict) -> dict:
        marca_id = _marca(x_marca_id)
        cliente_id = UUID(current_user["cliente_id"])
        rol = current_user.get("rol", "")
        return svc.generar_contenido(
            db=self.db,
            marca_id=marca_id,
            cliente_id=cliente_id,
            red_social=body.red_social,
            formato=body.formato,
            objetivo=body.objetivo,
            tono=body.tono,
            tema=body.tema,
            modo=body.modo,
            rol=rol,
        )

    def listar(self, x_marca_id: Optional[str], current_user: dict, estado: Optional[str] = None) -> dict:
        marca_id = _marca(x_marca_id)
        items = svc.listar(self.db, marca_id, estado=estado)
        return {"data": items, "count": len(items)}

    def usage(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        marca_id = _marca(x_marca_id)
        rol = current_user.get("rol", "")
        return svc.get_usage_info(self.db, marca_id, rol=rol)

    def versiones(self, contenido_id: UUID, x_marca_id: Optional[str], current_user: dict) -> dict:
        marca_id = _marca(x_marca_id)
        items = svc.obtener_versiones(self.db, contenido_id, marca_id)
        return {"data": items}

    def aprobar(self, contenido_id: UUID, body: AprobarRequest, x_marca_id: Optional[str], current_user: dict) -> dict:
        marca_id = _marca(x_marca_id)
        return feedback_svc.aprobar(self.db, contenido_id, marca_id, body.variante)

    def rechazar(self, contenido_id: UUID, body: RechazarRequest, x_marca_id: Optional[str], current_user: dict) -> dict:
        marca_id = _marca(x_marca_id)
        return feedback_svc.rechazar(self.db, contenido_id, marca_id, body.comentario)

    def editar(self, contenido_id: UUID, body: EditarRequest, x_marca_id: Optional[str], current_user: dict) -> dict:
        marca_id = _marca(x_marca_id)
        return feedback_svc.editar(self.db, contenido_id, marca_id, body.copy_editado, body.variante)

    def publicar_directo(self, contenido_id: UUID, body: PublicarDirectoRequest, x_marca_id: Optional[str], current_user: dict) -> dict:
        marca_id = _marca(x_marca_id)
        rol = current_user.get("rol", "")
        return svc.publicar_directo(self.db, marca_id, contenido_id, body.variante, rol=rol)

    def guardar_api_key(self, body: GuardarApiKeyRequest, current_user: dict) -> dict:
        cliente_id = UUID(current_user["cliente_id"])
        return svc.guardar_api_key(self.db, cliente_id, body.api_key)

    def listar_templates(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        marca_id = _marca(x_marca_id)
        items = svc.listar_templates(self.db, marca_id)
        return {"data": items, "count": len(items)}

    def crear_template(self, body: TemplateRequest, x_marca_id: Optional[str], current_user: dict) -> dict:
        marca_id = _marca(x_marca_id)
        data = body.model_dump()
        data["copy"] = data.pop("copy_text")
        return svc.crear_template(self.db, marca_id, data)

    def eliminar_template(self, template_id: UUID, x_marca_id: Optional[str], current_user: dict) -> dict:
        marca_id = _marca(x_marca_id)
        svc.eliminar_template(self.db, template_id, marca_id)
        return {"message": "Template eliminado"}
