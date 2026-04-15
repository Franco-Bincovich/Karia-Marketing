"""Entry point de KarIA Marketing API — FastAPI."""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import get_settings
from middleware.error_handler import register_error_handlers
from routes import (
    ads, analytics, auth, calendario, clientes, comunidad, contactos,
    contenido, feature_flags, onboarding, seo, social, usuarios,
)

logger = logging.getLogger(__name__)

VENCIMIENTO_CHECK_INTERVAL = 86400  # 24 horas en segundos


async def _vencimiento_loop():
    """Loop que ejecuta la verificación de vencimientos cada 24 horas."""
    from services.vencimiento_job import ejecutar_verificacion_vencimientos
    # Espera inicial de 60s para que la app termine de arrancar
    await asyncio.sleep(60)
    while True:
        try:
            logger.info("Ejecutando verificación de vencimientos...")
            ejecutar_verificacion_vencimientos()
        except Exception:
            logger.exception("Error en loop de vencimientos")
        await asyncio.sleep(VENCIMIENTO_CHECK_INTERVAL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Las tablas se gestionan via migraciones en Supabase — no crear aquí.
    task = asyncio.create_task(_vencimiento_loop())
    yield
    task.cancel()


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
    app.include_router(clientes.router)
    app.include_router(usuarios.router)
    app.include_router(feature_flags.router)
    app.include_router(contactos.router)
    app.include_router(contenido.router)
    app.include_router(calendario.router)
    app.include_router(social.router)
    app.include_router(ads.router)
    app.include_router(seo.router)
    app.include_router(analytics.router)
    app.include_router(comunidad.router)
    app.include_router(onboarding.router)

    @app.get("/health", tags=["system"])
    def health():
        return {"status": "ok", "service": "karia-marketing"}

    return app


app = create_app()
