"""Servicio de Automatizaciones — gestión de las 5 automatizaciones del sistema."""

import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from middleware.error_handler import AppError
from models.automatizacion_models import AutomatizacionMkt

logger = logging.getLogger(__name__)

# Definición de las 5 automatizaciones por defecto
DEFAULTS = [
    {"tipo": "vencimientos", "nombre": "Vencimientos", "descripcion": "Verifica vencimientos de clientes, pausa los vencidos y notifica a los 7 días.", "intervalo_horas": 24},
    {"tipo": "listening", "nombre": "Social Listening", "descripcion": "Escanea menciones de la marca en redes sociales y detecta crisis.", "intervalo_horas": 6},
    {"tipo": "reporte", "nombre": "Reporte Semanal", "descripcion": "Genera reporte automático de performance cada lunes.", "intervalo_horas": 168},
    {"tipo": "publicacion", "nombre": "Publicación Programada", "descripcion": "Revisa el calendario y publica posts programados via Zernio.", "intervalo_horas": 0.25},
    {"tipo": "orquestador", "nombre": "Orquestador", "descripcion": "Analiza métricas y ajusta plan de contenido y sugerencias estratégicas.", "intervalo_horas": 24},
]


def _s(a: AutomatizacionMkt) -> dict:
    return {
        "id": str(a.id), "marca_id": str(a.marca_id),
        "nombre": a.nombre, "descripcion": a.descripcion,
        "tipo": a.tipo, "activa": a.activa,
        "ultima_ejecucion": a.ultima_ejecucion.isoformat() if a.ultima_ejecucion else None,
        "proxima_ejecucion": a.proxima_ejecucion.isoformat() if a.proxima_ejecucion else None,
        "intervalo_horas": a.intervalo_horas,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    }


def inicializar_defaults(db: Session, marca_id: UUID):
    """Crea las 5 automatizaciones por defecto si no existen para la marca."""
    existentes = db.query(AutomatizacionMkt).filter(AutomatizacionMkt.marca_id == marca_id).count()
    if existentes >= 5:
        return
    for d in DEFAULTS:
        exists = db.query(AutomatizacionMkt).filter(
            AutomatizacionMkt.marca_id == marca_id, AutomatizacionMkt.tipo == d["tipo"],
        ).first()
        if not exists:
            db.add(AutomatizacionMkt(marca_id=marca_id, **d))
    db.flush()


def listar(db: Session, marca_id: UUID) -> list[dict]:
    """Lista las automatizaciones de la marca, creando defaults si faltan."""
    inicializar_defaults(db, marca_id)
    db.commit()
    rows = db.query(AutomatizacionMkt).filter(
        AutomatizacionMkt.marca_id == marca_id,
    ).order_by(AutomatizacionMkt.created_at).all()
    return [_s(r) for r in rows]


def activar(db: Session, marca_id: UUID, tipo: str) -> dict:
    obj = _get(db, marca_id, tipo)
    obj.activa = True
    db.commit()
    return _s(obj)


def desactivar(db: Session, marca_id: UUID, tipo: str) -> dict:
    obj = _get(db, marca_id, tipo)
    obj.activa = False
    db.commit()
    return _s(obj)


def ejecutar_ahora(db: Session, marca_id: UUID, tipo: str) -> dict:
    """Ejecuta manualmente una automatización."""
    obj = _get(db, marca_id, tipo)

    ejecutores = {
        "vencimientos": _ejecutar_vencimientos,
        "listening": _ejecutar_listening,
        "reporte": _ejecutar_reporte,
        "publicacion": _ejecutar_publicacion,
        "orquestador": _ejecutar_orquestador,
    }

    ejecutor = ejecutores.get(tipo)
    if not ejecutor:
        raise AppError(f"Automatización '{tipo}' no reconocida", "INVALID_TYPE", 400)

    resultado = ejecutor(db, marca_id)
    actualizar_ultima_ejecucion(db, marca_id, tipo)
    return {"tipo": tipo, "resultado": resultado}


def actualizar_ultima_ejecucion(db: Session, marca_id: UUID, tipo: str):
    """Actualiza timestamp de última ejecución y calcula próxima."""
    obj = db.query(AutomatizacionMkt).filter(
        AutomatizacionMkt.marca_id == marca_id, AutomatizacionMkt.tipo == tipo,
    ).first()
    if obj:
        ahora = datetime.now(timezone.utc)
        obj.ultima_ejecucion = ahora
        obj.proxima_ejecucion = ahora + timedelta(hours=obj.intervalo_horas)
        db.flush()
        db.commit()


def esta_activa(db: Session, marca_id: UUID, tipo: str) -> bool:
    """Chequea si una automatización está activa para una marca."""
    obj = db.query(AutomatizacionMkt).filter(
        AutomatizacionMkt.marca_id == marca_id, AutomatizacionMkt.tipo == tipo,
    ).first()
    return obj.activa if obj else True  # Default activa si no existe aún


def _get(db: Session, marca_id: UUID, tipo: str) -> AutomatizacionMkt:
    inicializar_defaults(db, marca_id)
    db.commit()
    obj = db.query(AutomatizacionMkt).filter(
        AutomatizacionMkt.marca_id == marca_id, AutomatizacionMkt.tipo == tipo,
    ).first()
    if not obj:
        raise AppError(f"Automatización '{tipo}' no encontrada", "NOT_FOUND", 404)
    return obj


# --- Ejecutores ---

def _ejecutar_vencimientos(db: Session, marca_id: UUID) -> str:
    from services.vencimiento_job import ejecutar_verificacion_vencimientos
    ejecutar_verificacion_vencimientos()
    return "Verificación de vencimientos ejecutada"


def _ejecutar_listening(db: Session, marca_id: UUID) -> str:
    from services.listening_service import buscar_menciones
    result = buscar_menciones(db, marca_id)
    return f"Escaneo completado: {result.get('menciones', 0)} menciones encontradas"


def _ejecutar_reporte(db: Session, marca_id: UUID) -> str:
    from services.reporting_service import generar_reporte
    generar_reporte(db, marca_id, "semanal")
    return "Reporte semanal generado"


def _ejecutar_publicacion(db: Session, marca_id: UUID) -> str:
    """Publica posts programados que ya llegaron a su hora."""
    from datetime import datetime, timezone
    from models.social_models import PublicacionesMkt
    from services import zernio_service
    from repositories import cuentas_sociales_repository as cuentas_repo

    ahora = datetime.now(timezone.utc)
    pendientes = db.query(PublicacionesMkt).filter(
        PublicacionesMkt.marca_id == marca_id,
        PublicacionesMkt.estado == "programado",
        PublicacionesMkt.programado_para <= ahora,
    ).all()

    publicados = 0
    for pub in pendientes:
        try:
            cuenta = cuentas_repo.obtener_por_red(db, marca_id, pub.red_social)
            if not cuenta:
                pub.estado = "fallido"
                pub.error_detalle = f"Sin cuenta de {pub.red_social} conectada"
                continue
            from integrations.zernio_client import publish_now
            result = publish_now(
                account_id=cuenta.account_id_externo,
                text=pub.copy_publicado or "",
                image_url=pub.imagen_url,
            )
            pub.estado = "publicado"
            pub.post_id_externo = result.get("external_post_id")
            pub.url_publicacion = result.get("url")
            pub.zernio_post_id = result.get("id")
            pub.publicado_at = ahora
            publicados += 1
        except Exception as e:
            pub.estado = "fallido"
            pub.error_detalle = str(e)[:200]
            logger.warning("Error publicando post %s: %s", pub.id, e)
    db.flush()
    db.commit()
    return f"{publicados} posts publicados de {len(pendientes)} programados"


def _ejecutar_orquestador(db: Session, marca_id: UUID) -> str:
    """Lee último reporte y métricas, ajusta plan de contenido y sugerencias."""
    from repositories import reportes_repository, memoria_marca_repository
    from services.estrategia_service import sugerir_acciones

    reportes = reportes_repository.listar(db, marca_id)
    ultimo = reportes[0] if reportes else None
    memoria_text = memoria_marca_repository.obtener_para_agente(db, marca_id)

    if not ultimo:
        return "Sin reportes disponibles — ejecutá un reporte primero"

    # Genera nuevas sugerencias basadas en el contexto
    entry = sugerir_acciones(db, marca_id)
    sugerencias = entry.get("contenido", {}).get("sugerencias", [])
    return f"Orquestador ejecutado: {len(sugerencias)} sugerencias generadas basadas en el último reporte"
