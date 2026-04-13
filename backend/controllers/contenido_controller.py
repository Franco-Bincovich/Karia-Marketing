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


# ── Schemas ──────────────────────────────────────────────────────────

class GenerarRequest(BaseModel):
    red_social: str
    formato: str
    objetivo: str
    tono: str
    tema: str
    memoria_marca: str = ""
    modo: str = "copilot"


class AprobarRequest(BaseModel):
    variante: str  # 'a' o 'b'


class RechazarRequest(BaseModel):
    comentario: str


class EditarRequest(BaseModel):
    copy_editado: str
    variante: str  # 'a' o 'b'


class TemplateRequest(BaseModel):
    nombre: str
    red_social: str
    formato: str
    copy: str
    hashtags: Optional[str] = None
    tono: Optional[str] = None
    objetivo: Optional[str] = None


# ── Helper ────────────────────────────────────────────────────────────

def _marca(x_marca_id: Optional[str]) -> UUID:
    if not x_marca_id:
        raise AppError("Header X-Marca-ID es requerido", "MISSING_MARCA_ID", 400)
    try:
        return UUID(x_marca_id)
    except ValueError:
        raise AppError("X-Marca-ID debe ser un UUID válido", "INVALID_MARCA_ID", 400)


# ── Controller ────────────────────────────────────────────────────────

class ContenidoController:
    def __init__(self, db: Session):
        self.db = db

    def generar(self, body: GenerarRequest, x_marca_id: Optional[str], current_user: dict) -> dict:
        """Genera variantes A/B. No requiere lógica extra — Claude siempre genera dos."""
        marca_id = _marca(x_marca_id)
        cliente_id = UUID(current_user["cliente_id"])
        return svc.generar_contenido(
            db=self.db, marca_id=marca_id, cliente_id=cliente_id,
            red_social=body.red_social, formato=body.formato,
            objetivo=body.objetivo, tono=body.tono, tema=body.tema,
            memoria_marca=body.memoria_marca, modo=body.modo,
        )

    def listar(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        marca_id = _marca(x_marca_id)
        items = svc.listar(self.db, marca_id)
        return {"data": items, "count": len(items)}

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

    def listar_templates(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        marca_id = _marca(x_marca_id)
        items = svc.listar_templates(self.db, marca_id)
        return {"data": items, "count": len(items)}

    def crear_template(self, body: TemplateRequest, x_marca_id: Optional[str], current_user: dict) -> dict:
        marca_id = _marca(x_marca_id)
        return svc.crear_template(self.db, marca_id, body.model_dump())

    def eliminar_template(self, template_id: UUID, x_marca_id: Optional[str], current_user: dict) -> dict:
        marca_id = _marca(x_marca_id)
        svc.eliminar_template(self.db, template_id, marca_id)
        return {"message": "Template eliminado"}
