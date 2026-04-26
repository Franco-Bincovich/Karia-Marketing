"""Adaptador HTTP para auth_service: transforma Request/Response."""

from typing import Optional

from fastapi import Request
from pydantic import BaseModel, EmailStr

from middleware.error_handler import AppError
from services.auth_service import AuthService


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthController:
    """Convierte requests HTTP en llamadas al AuthService."""

    def __init__(self, db):
        self.service = AuthService(db)

    def login(self, body: LoginRequest, request: Request) -> dict:
        """Maneja POST /api/auth/login."""
        ip = _get_ip(request)
        user_agent = request.headers.get("user-agent")
        return self.service.login(body.email, body.password, ip=ip, user_agent=user_agent)

    def logout(self, token: str, request: Request) -> dict:
        """Maneja POST /api/auth/logout."""
        ip = _get_ip(request)
        self.service.logout(token, ip=ip)
        return {"message": "Sesión cerrada correctamente"}

    def me(self, payload: dict) -> dict:
        """Maneja GET /api/auth/me."""
        if not payload:
            raise AppError("No autenticado", "UNAUTHORIZED", 401)
        return self.service.get_me(payload)


def _get_ip(request: Request) -> Optional[str]:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return None
