"""Cliente de email usando Resend API."""

import logging

import requests

from config.settings import get_settings

logger = logging.getLogger(__name__)

_RESEND_URL = "https://api.resend.com/emails"


def _send(to: str, subject: str, html: str) -> bool:
    """Envía un email via Resend. Retorna True si se envió, False si falló."""
    settings = get_settings()
    if not settings.RESEND_API_KEY:
        logger.warning("[email] RESEND_API_KEY no configurada — email no enviado a %s", to)
        return False

    try:
        resp = requests.post(
            _RESEND_URL,
            headers={
                "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from": settings.EMAIL_FROM,
                "to": [to],
                "subject": subject,
                "html": html,
            },
            timeout=15,
        )
        if resp.status_code in (200, 201):
            logger.info("[email] enviado a %s — subject: %s", to, subject)
            return True
        logger.error("[email] error %s enviando a %s — %s", resp.status_code, to, resp.text[:200])
        return False
    except Exception:
        logger.exception("[email] error de conexión enviando a %s", to)
        return False


def send_welcome_email(email: str, password: str, nombre: str) -> bool:
    """Email de bienvenida con credenciales de acceso."""
    return _send(
        to=email,
        subject="Bienvenido a Nexo Marketing",
        html=(
            f"<h2>Hola {nombre},</h2>"
            f"<p>Tu cuenta en Nexo Marketing fue creada correctamente.</p>"
            f"<p><strong>Email:</strong> {email}<br>"
            f"<strong>Contraseña temporal:</strong> {password}</p>"
            f"<p>Ingresá y cambiá tu contraseña lo antes posible.</p>"
            f"<p>— Equipo Nexo</p>"
        ),
    )


def send_expiration_warning_email(email: str, fecha_vencimiento: str, nombre: str) -> bool:
    """Aviso de que la membresía vence en 7 días."""
    return _send(
        to=email,
        subject="Tu membresía en Nexo vence en 7 días",
        html=(
            f"<h2>Hola {nombre},</h2>"
            f"<p>Tu membresía en Nexo Marketing vence el <strong>{fecha_vencimiento}</strong>.</p>"
            f"<p>Contactá a tu administrador para renovar y mantener el acceso a la plataforma.</p>"
            f"<p>— Equipo Nexo</p>"
        ),
    )


def send_account_paused_email(email: str, nombre: str) -> bool:
    """Notificación de que la cuenta fue pausada por vencimiento."""
    return _send(
        to=email,
        subject="Tu cuenta en Nexo fue pausada",
        html=(
            f"<h2>Hola {nombre},</h2>"
            f"<p>Tu membresía en Nexo Marketing venció y tu cuenta fue pausada automáticamente.</p>"
            f"<p>Contactá a tu administrador para renovar y reactivar el acceso.</p>"
            f"<p>— Equipo Nexo</p>"
        ),
    )
