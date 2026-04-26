"""Utilidades de seguridad: hashing, JWT, HMAC y cifrado Fernet."""

import hashlib
import hmac
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import bcrypt
import jwt

from config.settings import get_settings

logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """Genera hash bcrypt de la contraseña."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verifica una contraseña contra su hash bcrypt."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(payload: Dict[str, Any], expires_hours: Optional[int] = None) -> str:
    """Genera un JWT firmado con expiración configurable."""
    settings = get_settings()
    hours = expires_hours or settings.JWT_EXPIRATION_HOURS
    exp = datetime.now(timezone.utc) + timedelta(hours=hours)
    data = {**payload, "exp": exp, "iat": datetime.now(timezone.utc)}
    return jwt.encode(data, settings.JWT_SECRET, algorithm="HS256")


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decodifica y valida un JWT. Lanza jwt.PyJWTError si inválido."""
    settings = get_settings()
    return jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])


def hash_token(token: str) -> str:
    """Hash SHA-256 de un token para almacenamiento seguro."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def sign_hmac(data: str) -> str:
    """Firma un string con HMAC-SHA256 usando SECRET_KEY."""
    settings = get_settings()
    return hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        data.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def encrypt_token(plaintext: str) -> str:
    """Encripta un access token con Fernet usando ENCRYPTION_KEY del .env."""
    from middleware.error_handler import AppError

    key = get_settings().ENCRYPTION_KEY
    if not key:
        raise AppError(
            'ENCRYPTION_KEY no configurada. Generá una con: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"',
            "ENCRYPTION_KEY_MISSING",
            500,
        )
    from cryptography.fernet import Fernet

    return Fernet(key.encode()).encrypt(plaintext.encode()).decode()


def decrypt_token(ciphertext: str) -> str:
    """Desencripta un token Fernet. Falla si falta ENCRYPTION_KEY."""
    from middleware.error_handler import AppError

    key = get_settings().ENCRYPTION_KEY
    if not key:
        raise AppError("ENCRYPTION_KEY no configurada — no se puede desencriptar", "ENCRYPTION_KEY_MISSING", 500)
    from cryptography.fernet import Fernet

    return Fernet(key.encode()).decrypt(ciphertext.encode()).decode()
