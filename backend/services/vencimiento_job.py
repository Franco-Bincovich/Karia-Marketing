"""Job diario de verificación de vencimientos de clientes."""

import logging

from sqlalchemy.orm import Session

from integrations.database import SessionLocal
from repositories.clientes_repository import ClientesRepository

logger = logging.getLogger(__name__)


def ejecutar_verificacion_vencimientos():
    """
    Corre una vez al día. Hace dos cosas:
    1. Clientes que vencen en 7 días → marca notificacion_enviada = True
    2. Clientes activos cuyo vencimiento ya pasó → pausa automática
    """
    db: Session = SessionLocal()
    try:
        repo = ClientesRepository(db)

        # 1. Notificar clientes por vencer (7 días)
        por_vencer = repo.list_por_vencer(dias=7)
        for cliente in por_vencer:
            cliente.notificacion_enviada = True
            logger.info(
                "Cliente %s (%s) vence en 7 días — notificación marcada",
                cliente.nombre, cliente.email_admin,
            )
            # TODO: Enviar email de aviso de vencimiento
            # send_expiration_warning_email(cliente.email_admin, cliente.fecha_vencimiento)

        # 2. Pausar clientes vencidos
        vencidos = repo.list_vencidos()
        for cliente in vencidos:
            cliente.activo = False
            logger.info(
                "Cliente %s (%s) vencido — pausado automáticamente",
                cliente.nombre, cliente.email_admin,
            )
            # TODO: Enviar email de cuenta pausada
            # send_account_paused_email(cliente.email_admin)

        db.commit()
        logger.info(
            "Verificación de vencimientos: %d notificados, %d pausados",
            len(por_vencer), len(vencidos),
        )
    except Exception:
        db.rollback()
        logger.exception("Error en verificación de vencimientos")
    finally:
        db.close()
