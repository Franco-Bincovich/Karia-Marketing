"""Handler global de errores con formato estándar de respuesta."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import jwt


class AppError(Exception):
    """Error de aplicación con código HTTP y código de error."""

    def __init__(self, message: str, code: str = "APP_ERROR", status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


def _error_response(message: str, code: str, status: int) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={"error": True, "message": message, "code": code},
    )


def register_error_handlers(app: FastAPI) -> None:
    """Registra todos los handlers de error en la app FastAPI."""

    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError):
        return _error_response(exc.message, exc.code, exc.status_code)

    @app.exception_handler(jwt.ExpiredSignatureError)
    async def handle_jwt_expired(request: Request, exc: jwt.ExpiredSignatureError):
        return _error_response("Token expirado", "TOKEN_EXPIRED", 401)

    @app.exception_handler(jwt.PyJWTError)
    async def handle_jwt_error(request: Request, exc: jwt.PyJWTError):
        return _error_response("Token inválido", "TOKEN_INVALID", 401)

    @app.exception_handler(ValueError)
    async def handle_value_error(request: Request, exc: ValueError):
        return _error_response(str(exc), "VALIDATION_ERROR", 422)

    @app.exception_handler(Exception)
    async def handle_generic_error(request: Request, exc: Exception):
        return _error_response("Error interno del servidor", "INTERNAL_ERROR", 500)
