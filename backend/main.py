"""Entry point de KarIA Marketing API — FastAPI."""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import get_settings
from middleware.error_handler import register_error_handlers
from routes import (
    ads, agentes, analytics, auth, calendario, clientes, comunidad, contactos,
    contenido, estrategia, feature_flags, imagenes, listening, onboarding,
    reporting, seo, social, usuarios,
)

logger = logging.getLogger(__name__)

VENCIMIENTO_CHECK_INTERVAL = 86400  # 24 horas
LISTENING_CHECK_INTERVAL = 21600    # 6 horas


async def _vencimiento_loop():
    """Loop de verificación de vencimientos cada 24 horas."""
    from services.vencimiento_job import ejecutar_verificacion_vencimientos
    await asyncio.sleep(60)
    while True:
        try:
            logger.info("Ejecutando verificación de vencimientos...")
            ejecutar_verificacion_vencimientos()
        except Exception:
            logger.exception("Error en loop de vencimientos")
        await asyncio.sleep(VENCIMIENTO_CHECK_INTERVAL)


async def _listening_loop():
    """Loop de escaneo de menciones cada 6 horas."""
    await asyncio.sleep(120)
    while True:
        try:
            logger.info("Ejecutando escaneo de listening...")
            from integrations.database import SessionLocal
            from services.listening_service import buscar_menciones
            from models.cliente_models import MarcaMkt
            db = SessionLocal()
            try:
                marcas = db.query(MarcaMkt).filter(MarcaMkt.activa == True).all()  # noqa: E712
                for marca in marcas:
                    try:
                        buscar_menciones(db, marca.id)
                    except Exception:
                        logger.exception("Error scanning marca %s", marca.id)
            finally:
                db.close()
        except Exception:
            logger.exception("Error en loop de listening")
        await asyncio.sleep(LISTENING_CHECK_INTERVAL)


REPORTING_WEEKLY_INTERVAL = 86400  # Check daily, generate on Mondays


async def _reporting_loop():
    """Genera reporte semanal automático cada lunes."""
    await asyncio.sleep(180)
    while True:
        try:
            from datetime import date
            if date.today().weekday() == 0:  # Monday
                logger.info("Lunes — generando reportes semanales...")
                from integrations.database import SessionLocal
                from services.reporting_service import generar_reporte
                from models.cliente_models import MarcaMkt
                db = SessionLocal()
                try:
                    marcas = db.query(MarcaMkt).filter(MarcaMkt.activa == True).all()  # noqa: E712
                    for marca in marcas:
                        try:
                            generar_reporte(db, marca.id, "semanal")
                        except Exception:
                            logger.exception("Error generando reporte para marca %s", marca.id)
                finally:
                    db.close()
        except Exception:
            logger.exception("Error en loop de reporting")
        await asyncio.sleep(REPORTING_WEEKLY_INTERVAL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task_venc = asyncio.create_task(_vencimiento_loop())
    task_listen = asyncio.create_task(_listening_loop())
    task_report = asyncio.create_task(_reporting_loop())
    yield
    task_venc.cancel()
    task_listen.cancel()
    task_report.cancel()


def create_app() -> FastAPI:
    """Factory de la aplicación FastAPI."""
    settings = get_settings()

    app = FastAPI(
        title="KarIA Marketing API",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_error_handlers(app)

    app.include_router(auth.router)
    app.include_router(agentes.router)
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

    @app.get("/health", tags=["system"])
    def health():
        return {"status": "ok", "service": "karia-marketing"}

    return app


app = create_app()
