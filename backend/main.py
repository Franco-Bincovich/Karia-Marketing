"""Entry point de Nexo Marketing API — FastAPI."""

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import date

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from config.settings import get_settings
from middleware.error_handler import register_error_handlers
from routes import (
    ads,
    agentes,
    analytics,
    api_keys,
    auth,
    automatizaciones,
    calendario,
    clientes,
    comunidad,
    contactos,
    contenido,
    estrategia,
    feature_flags,
    imagenes,
    listening,
    onboarding,
    organigrama,
    reporting,
    seo,
    social,
    usuarios,
)

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

# Intervalos de automatizaciones (en segundos)
INTERVAL_VENCIMIENTOS = 86400  # 24 horas
INTERVAL_LISTENING = 21600  # 6 horas
INTERVAL_REPORTE = 86400  # 24 horas (ejecuta solo lunes)
INTERVAL_PUBLICACION = 900  # 15 minutos
INTERVAL_ORQUESTADOR = 86400  # 24 horas


def _get_marcas_activas(db):
    """Helper: obtiene todas las marcas activas."""
    from repositories.clientes_repository import listar_marcas_activas

    return listar_marcas_activas(db)


def _check_activa(db, marca_id, tipo: str) -> bool:
    """Chequea si la automatización está activa para la marca."""
    from services.automatizaciones_service import esta_activa

    return esta_activa(db, marca_id, tipo)


def _actualizar_ejecucion(db, marca_id, tipo: str):
    """Actualiza timestamp de última ejecución."""
    from services.automatizaciones_service import actualizar_ultima_ejecucion

    actualizar_ultima_ejecucion(db, marca_id, tipo)


# --- Automatización: Vencimientos (24h) ---


async def _automatizacion_vencimientos():
    """Automatización de verificación de vencimientos cada 24 horas."""
    from services.vencimiento_job import ejecutar_verificacion_vencimientos

    await asyncio.sleep(60)
    while True:
        try:
            logger.info("[automatización] Ejecutando vencimientos...")
            ejecutar_verificacion_vencimientos()
        except Exception:
            logger.exception("[automatización] Error en vencimientos")
        await asyncio.sleep(INTERVAL_VENCIMIENTOS)


# --- Automatización: Social Listening (6h) ---


async def _automatizacion_listening():
    """Automatización de escaneo de menciones cada 6 horas."""
    await asyncio.sleep(120)
    while True:
        try:
            logger.info("[automatización] Ejecutando listening...")
            from integrations.database import SessionLocal
            from services.listening_service import buscar_menciones

            db = SessionLocal()
            try:
                for marca in _get_marcas_activas(db):
                    if _check_activa(db, marca.id, "listening"):
                        try:
                            buscar_menciones(db, marca.id)
                            _actualizar_ejecucion(db, marca.id, "listening")
                        except Exception:
                            logger.exception("[automatización] Error listening marca %s", marca.id)
            finally:
                db.close()
        except Exception:
            logger.exception("[automatización] Error en listening")
        await asyncio.sleep(INTERVAL_LISTENING)


# --- Automatización: Reporte Semanal (lunes) ---


async def _automatizacion_reporte():
    """Automatización de reporte semanal cada lunes."""
    await asyncio.sleep(180)
    while True:
        try:
            if date.today().weekday() == 0:  # Lunes
                logger.info("[automatización] Lunes — generando reportes semanales...")
                from integrations.database import SessionLocal
                from services.reporting_service import generar_reporte

                db = SessionLocal()
                try:
                    for marca in _get_marcas_activas(db):
                        if _check_activa(db, marca.id, "reporte"):
                            try:
                                generar_reporte(db, marca.id, "semanal")
                                _actualizar_ejecucion(db, marca.id, "reporte")
                            except Exception:
                                logger.exception("[automatización] Error reporte marca %s", marca.id)
                finally:
                    db.close()
        except Exception:
            logger.exception("[automatización] Error en reporte")
        await asyncio.sleep(INTERVAL_REPORTE)


# --- Automatización: Publicación Programada (15 min) ---


async def _automatizacion_publicacion():
    """Automatización de publicación de posts programados cada 15 minutos."""
    await asyncio.sleep(90)
    while True:
        try:
            from integrations.database import SessionLocal
            from services.automatizaciones_service import _ejecutar_publicacion

            db = SessionLocal()
            try:
                for marca in _get_marcas_activas(db):
                    if _check_activa(db, marca.id, "publicacion"):
                        try:
                            _ejecutar_publicacion(db, marca.id)
                            _actualizar_ejecucion(db, marca.id, "publicacion")
                        except Exception:
                            logger.exception("[automatización] Error publicación marca %s", marca.id)
            finally:
                db.close()
        except Exception:
            logger.exception("[automatización] Error en publicación")
        await asyncio.sleep(INTERVAL_PUBLICACION)


# --- Automatización: Orquestador (24h) ---


async def _automatizacion_orquestador():
    """Automatización del orquestador cada 24 horas."""
    await asyncio.sleep(240)
    while True:
        try:
            logger.info("[automatización] Ejecutando orquestador...")
            from integrations.database import SessionLocal
            from services.automatizaciones_service import _ejecutar_orquestador

            db = SessionLocal()
            try:
                for marca in _get_marcas_activas(db):
                    if _check_activa(db, marca.id, "orquestador"):
                        try:
                            _ejecutar_orquestador(db, marca.id)
                            _actualizar_ejecucion(db, marca.id, "orquestador")
                        except Exception:
                            logger.exception("[automatización] Error orquestador marca %s", marca.id)
            finally:
                db.close()
        except Exception:
            logger.exception("[automatización] Error en orquestador")
        await asyncio.sleep(INTERVAL_ORQUESTADOR)


@asynccontextmanager
async def lifespan(app: FastAPI):
    tasks = [
        asyncio.create_task(_automatizacion_vencimientos()),
        asyncio.create_task(_automatizacion_listening()),
        asyncio.create_task(_automatizacion_reporte()),
        asyncio.create_task(_automatizacion_publicacion()),
        asyncio.create_task(_automatizacion_orquestador()),
    ]
    yield
    for t in tasks:
        t.cancel()


def _rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"message": "Demasiados intentos. Esperá un momento.", "code": "RATE_LIMITED"},
    )


def create_app() -> FastAPI:
    """Factory de la aplicación FastAPI."""
    settings = get_settings()
    is_prod = settings.ENV == "production"

    app = FastAPI(
        title="Nexo Marketing API",
        version="1.0.0",
        lifespan=lifespan,
        docs_url=None if is_prod else "/docs",
        redoc_url=None if is_prod else "/redoc",
        openapi_url=None if is_prod else "/openapi.json",
    )

    # Rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-Marca-ID", "X-Request-ID"],
    )

    register_error_handlers(app)

    app.include_router(auth.router)
    app.include_router(agentes.router)
    app.include_router(api_keys.router)
    app.include_router(automatizaciones.router)
    app.include_router(clientes.router)
    app.include_router(usuarios.router)
    app.include_router(feature_flags.router)
    app.include_router(contactos.router)
    app.include_router(contenido.router)
    app.include_router(estrategia.router)
    app.include_router(imagenes.router)
    app.include_router(listening.router)
    app.include_router(calendario.router)
    app.include_router(social.router)
    app.include_router(ads.router)
    app.include_router(seo.router)
    app.include_router(analytics.router)
    app.include_router(reporting.router)
    app.include_router(comunidad.router)
    app.include_router(onboarding.router)
    app.include_router(organigrama.router)

    @app.get("/health", tags=["system"])
    def health():
        return {"status": "ok", "service": "nexo-marketing"}

    return app


app = create_app()
