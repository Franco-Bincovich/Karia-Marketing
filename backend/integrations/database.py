"""Conexión SQLAlchemy agnóstica al proveedor de base de datos."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from config.settings import get_settings


class Base(DeclarativeBase):
    pass


def _build_engine():
    """Construye el engine SQLAlchemy desde DATABASE_URL. La conexión es lazy:
    no se abre un socket hasta la primera query real."""
    settings = get_settings()
    return create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
    )


engine = _build_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency injection: provee sesión de base de datos y garantiza cierre."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
