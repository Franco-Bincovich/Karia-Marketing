"""Rutas de autenticación: login, logout, me."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from controllers.auth_controller import AuthController, LoginRequest
from integrations.database import get_db
from middleware.auth import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])
_bearer = HTTPBearer(auto_error=False)
_limiter = Limiter(key_func=get_remote_address)


@router.post("/login")
@_limiter.limit("5/minute")
def login(body: LoginRequest, request: Request, db: Session = Depends(get_db)):
    """Autentica al usuario y retorna JWT. Set-Cookie httpOnly incluido."""
    result = AuthController(db).login(body, request)
    # Agregar cookie httpOnly además del token en body
    response = JSONResponse(content=result)
    token = result.get("access_token", "")
    if token:
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=86400,
        )
    return response


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
