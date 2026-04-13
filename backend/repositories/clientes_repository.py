"""Repositorio de acceso a datos para clientes_mkt y marcas_mkt."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from models.cliente_models import ClienteMkt, MarcaMkt


class ClientesRepository:
    """CRUD puro sin lógica de negocio para clientes y marcas."""

    def __init__(self, db: Session):
        self.db = db

    def get_cliente_by_id(self, cliente_id: UUID) -> Optional[ClienteMkt]:
        """Obtiene un cliente por ID."""
        return self.db.query(ClienteMkt).filter(ClienteMkt.id == cliente_id).first()

    def get_cliente_by_email(self, email: str) -> Optional[ClienteMkt]:
        """Obtiene un cliente por email de administrador."""
        return self.db.query(ClienteMkt).filter(ClienteMkt.email_admin == email).first()

    def list_clientes(self) -> List[ClienteMkt]:
        """Lista todos los clientes activos."""
        return self.db.query(ClienteMkt).filter(ClienteMkt.activo == True).all()  # noqa: E712

    def create_cliente(self, data: dict) -> ClienteMkt:
        """Crea un nuevo cliente."""
        cliente = ClienteMkt(**data)
        self.db.add(cliente)
        self.db.flush()
        return cliente

    def update_cliente(self, cliente_id: UUID, data: dict) -> Optional[ClienteMkt]:
        """Actualiza campos de un cliente."""
        cliente = self.get_cliente_by_id(cliente_id)
        if not cliente:
            return None
        for key, value in data.items():
            setattr(cliente, key, value)
        self.db.flush()
        return cliente

    def get_marca_by_id(self, marca_id: UUID) -> Optional[MarcaMkt]:
        """Obtiene una marca por ID."""
        return self.db.query(MarcaMkt).filter(MarcaMkt.id == marca_id).first()

    def list_marcas_by_cliente(self, cliente_id: UUID) -> List[MarcaMkt]:
        """Lista todas las marcas activas de un cliente."""
        return self.db.query(MarcaMkt).filter(
            MarcaMkt.cliente_id == cliente_id,
            MarcaMkt.activa == True,  # noqa: E712
        ).all()

    def create_marca(self, data: dict) -> MarcaMkt:
        """Crea una nueva marca."""
        marca = MarcaMkt(**data)
        self.db.add(marca)
        self.db.flush()
        return marca

    def update_marca(self, marca_id: UUID, data: dict) -> Optional[MarcaMkt]:
        """Actualiza campos de una marca."""
        marca = self.get_marca_by_id(marca_id)
        if not marca:
            return None
        for key, value in data.items():
            setattr(marca, key, value)
        self.db.flush()
        return marca
