"""Rutas de autenticación: login, logout, me."""

from fastapi import APIRouter, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from controllers.auth_controller import AuthController, LoginRequest
from integrations.database import get_db
from middleware.auth import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])
_bearer = HTTPBearer(auto_error=False)


@router.post("/login")
def login(body: LoginRequest, request: Request, db: Session = Depends(get_db)):
    """Autentica al usuario y retorna JWT."""
    return AuthController(db).login(body, request)


@router.post("/logout")
def logout(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: Session = Depends(get_db),
):
    """Invalida la sesión del usuario autenticado."""
    token = credentials.credentials if credentials else ""
    return AuthController(db).logout(token, request)


@router.get("/me")
def me(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retorna los datos del usuario autenticado."""
    return AuthController(db).me(current_user)
