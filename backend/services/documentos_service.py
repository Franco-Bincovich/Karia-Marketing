"""Servicio de documentos de marca — upload, extracción de texto, listado."""

import io
import logging
from typing import Optional
from uuid import UUID

import requests
from sqlalchemy.orm import Session

from config.settings import get_settings
from middleware.error_handler import AppError
from models.documento_models import DocumentoMarcaMkt

logger = logging.getLogger(__name__)

ALLOWED_TYPES = {".pdf", ".docx", ".doc", ".txt"}
MAX_SIZE = 10 * 1024 * 1024  # 10MB


def _extract_text(content: bytes, filename: str) -> str:
    """Extrae texto del archivo según su extensión."""
    ext = _get_ext(filename)

    if ext == ".txt":
        return content.decode("utf-8", errors="replace")

    if ext == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(content))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages).strip()

    if ext in (".docx", ".doc"):
        from docx import Document

        doc = Document(io.BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs).strip()

    return ""


def _get_ext(filename: str) -> str:
    return "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def _upload_to_storage(content: bytes, marca_id: UUID, filename: str) -> Optional[str]:
    """Sube documento a Supabase Storage."""
    settings = get_settings()
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
        logger.warning("[docs] Supabase Storage no configurado")
        return None

    bucket = "Nexo - Marketing - Documents"
    path = f"{marca_id}/{filename}"
    base_url = settings.SUPABASE_URL.rstrip("/")

    if "supabase.com/dashboard" in base_url:
        ref = base_url.split("/")[-1]
        storage_url = f"https://{ref}.supabase.co/storage/v1/object/{bucket}/{path}"
    else:
        storage_url = f"{base_url}/storage/v1/object/{bucket}/{path}"

    resp = requests.post(
        storage_url,
        headers={"Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}", "Content-Type": "application/octet-stream"},
        data=content,
        timeout=30,
    )

    if resp.status_code in (200, 201):
        return storage_url.replace("/object/", "/object/public/")

    logger.warning("[docs] upload failed %s", resp.status_code)
    return None


def _delete_from_storage(url_storage: Optional[str]):
    """Elimina archivo de Supabase Storage."""
    if not url_storage:
        return
    settings = get_settings()
    if not settings.SUPABASE_SERVICE_KEY:
        return
    delete_url = url_storage.replace("/object/public/", "/object/")
    try:
        requests.delete(delete_url, headers={"Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}"}, timeout=10)
    except Exception:
        logger.warning("[docs] Error eliminando de storage")


def subir(db: Session, marca_id: UUID, filename: str, content: bytes) -> dict:
    """Sube documento, extrae texto, guarda en DB."""
    ext = _get_ext(filename)
    if ext not in ALLOWED_TYPES:
        raise AppError(f"Formato no soportado: {ext}. Usar PDF, DOCX o TXT.", "INVALID_FILE_TYPE", 400)

    if len(content) > MAX_SIZE:
        raise AppError("El archivo excede el límite de 10MB.", "FILE_TOO_LARGE", 400)

    texto = _extract_text(content, filename)
    url = _upload_to_storage(content, marca_id, filename)

    doc = DocumentoMarcaMkt(
        marca_id=marca_id,
        nombre_archivo=filename,
        tipo=ext.lstrip("."),
        url_storage=url,
        texto_extraido=texto,
    )
    db.add(doc)
    db.flush()
    db.commit()

    logger.info("[docs] subido — %s (%d chars extraídos)", filename, len(texto))
    return _s(doc)


def listar(db: Session, marca_id: UUID) -> list[dict]:
    rows = (
        db.query(DocumentoMarcaMkt)
        .filter(
            DocumentoMarcaMkt.marca_id == marca_id,
        )
        .order_by(DocumentoMarcaMkt.created_at.desc())
        .all()
    )
    return [_s(r) for r in rows]


def eliminar(db: Session, doc_id: UUID, marca_id: UUID) -> bool:
    obj = (
        db.query(DocumentoMarcaMkt)
        .filter(
            DocumentoMarcaMkt.id == doc_id,
            DocumentoMarcaMkt.marca_id == marca_id,
        )
        .first()
    )
    if not obj:
        raise AppError("Documento no encontrado", "NOT_FOUND", 404)
    _delete_from_storage(obj.url_storage)
    db.delete(obj)
    db.commit()
    return True


def obtener_textos(db: Session, marca_id: UUID) -> str:
    """Retorna todos los textos extraídos concatenados para contexto de agentes."""
    rows = (
        db.query(DocumentoMarcaMkt)
        .filter(
            DocumentoMarcaMkt.marca_id == marca_id,
            DocumentoMarcaMkt.texto_extraido.isnot(None),
        )
        .all()
    )
    if not rows:
        return ""
    return "\n\n---\n\n".join(f"[{r.nombre_archivo}]\n{r.texto_extraido}" for r in rows if r.texto_extraido)


def _s(d: DocumentoMarcaMkt) -> dict:
    return {
        "id": str(d.id),
        "marca_id": str(d.marca_id),
        "nombre_archivo": d.nombre_archivo,
        "tipo": d.tipo,
        "url_storage": d.url_storage,
        "tiene_texto": bool(d.texto_extraido),
        "chars_extraidos": len(d.texto_extraido) if d.texto_extraido else 0,
        "created_at": d.created_at.isoformat() if d.created_at else None,
    }
