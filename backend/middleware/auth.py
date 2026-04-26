"""Middleware de autenticación JWT con control de roles."""

from typing import Optional

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from integrations.database import get_db
from middleware.error_handler import AppError
from utils.security import decode_access_token

security = HTTPBearer(auto_error=False)

PUBLIC_ROUTES = {
    ("POST", "/api/auth/login"),
    ("GET", "/health"),
    ("GET", "/docs"),
    ("GET", "/openapi.json"),
    ("GET", "/redoc"),
}


def _extract_token(request: Request, credentials: Optional[HTTPAuthorizationCredentials]) -> str:
    """Extrae token de: 1) cookie httpOnly (prioritario) 2) header Authorization."""
    # 1. Cookie httpOnly
    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        return cookie_token
    # 2. Header Authorization: Bearer <token>
    if credentials and credentials.credentials:
        return credentials.credentials
    raise AppError("No autenticado", "UNAUTHORIZED", 401)


def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> dict:
    """Extrae y valida el JWT; retorna el payload del usuario actual."""
    route_key = (request.method, request.url.path)
    if route_key in PUBLIC_ROUTES:
        return {}

    token = _extract_token(request, credentials)
    payload = decode_access_token(token)

    if not payload.get("sub"):
        raise AppError("Token sin usuario", "TOKEN_INVALID", 401)

    return payload


def require_roles(*roles: str):
    """Dependencia que exige que el usuario tenga uno de los roles indicados."""

    def checker(current_user: dict = Depends(get_current_user)) -> dict:
        if not current_user:
            raise AppError("No autenticado", "UNAUTHORIZED", 401)
        user_role = current_user.get("rol")
        if user_role not in roles:
            raise AppError("Acceso denegado", "FORBIDDEN", 403)
        return current_user

    return checker


def require_superadmin():
    return require_roles("superadmin")


def require_admin_or_above():
    return require_roles("superadmin", "admin")
