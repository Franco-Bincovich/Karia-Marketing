"""Entry point de KarIA Marketing API — FastAPI."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import get_settings
from middleware.error_handler import register_error_handlers
from routes import auth, clientes, contactos, feature_flags, usuarios


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Las tablas se gestionan via migraciones en Supabase — no crear aquí.
    yield


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

    @app.get("/health", tags=["system"])
    def health():
        return {"status": "ok", "service": "karia-marketing"}

    return app


app = create_app()
