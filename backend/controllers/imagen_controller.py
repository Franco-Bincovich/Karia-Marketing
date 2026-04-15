"""Adaptador HTTP para el módulo de Imágenes IA."""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.orm import Session

from middleware.error_handler import AppError
from services import imagen_service as svc


class GenerarImagenRequest(BaseModel):
    descripcion: str
    tamano: str = "1024x1024"
    estilo: str = "vivid"
    usar_perfil_marca: bool = True


class GenerarParaContenidoRequest(BaseModel):
    tamano: str = "1024x1024"
    estilo: str = "vivid"


class GuardarOpenAIKeyRequest(BaseModel):
    api_key: str


def _marca(x_marca_id: Optional[str]) -> UUID:
    if not x_marca_id:
        raise AppError("Header X-Marca-ID es requerido", "MISSING_MARCA_ID", 400)
    try:
        return UUID(x_marca_id)
    except ValueError:
        raise AppError("X-Marca-ID debe ser un UUID válido", "INVALID_MARCA_ID", 400)


class ImagenController:
    def __init__(self, db: Session):
        self.db = db

    def generar(self, body: GenerarImagenRequest, x_marca_id: Optional[str], current_user: dict) -> dict:
        marca_id = _marca(x_marca_id)
        rol = current_user.get("rol", "")
        return svc.generar(
            self.db, marca_id, body.descripcion,
            tamano=body.tamano, estilo=body.estilo,
            usar_perfil=body.usar_perfil_marca, rol=rol,
        )

    def generar_para_contenido(self, contenido_id: UUID, body: GenerarParaContenidoRequest,
                               x_marca_id: Optional[str], current_user: dict) -> dict:
        marca_id = _marca(x_marca_id)
        rol = current_user.get("rol", "")
        return svc.generar_para_contenido(
            self.db, marca_id, contenido_id,
            tamano=body.tamano, estilo=body.estilo, rol=rol,
        )

    def listar(self, x_marca_id: Optional[str], current_user: dict) -> dict:
        marca_id = _marca(x_marca_id)
        items = svc.listar(self.db, marca_id)
        return {"data": items, "count": len(items)}

    def asociar(self, imagen_id: UUID, contenido_id: UUID,
                x_marca_id: Optional[str], current_user: dict) -> dict:
        marca_id = _marca(x_marca_id)
        return svc.asociar_contenido(self.db, marca_id, imagen_id, contenido_id)

    def guardar_key(self, body: GuardarOpenAIKeyRequest, current_user: dict) -> dict:
        cliente_id = UUID(current_user["cliente_id"])
        # Superadmin can always save
        rol = current_user.get("rol", "")
        plan = "Premium" if rol == "superadmin" else current_user.get("plan", "Basic")
        return svc.guardar_openai_key(self.db, cliente_id, body.api_key, plan)
