"""Importa todos los modelos para que SQLAlchemy los registre correctamente."""

from models.cliente_models import ClienteMkt, MarcaMkt  # noqa: F401
from models.auth_models import UsuarioMkt, SesionMkt, UsuarioMarcaMkt  # noqa: F401
from models.permisos_models import PermisoMkt, FeatureFlagMkt, OnboardingMkt, AuditoriaMkt  # noqa: F401
from models.contacto_models import ContactoMkt  # noqa: F401
from models.contenido_models import ContenidoMkt, VersionesContenidoMkt, AprendizajeMkt, TemplatesMkt  # noqa: F401
from models.social_models import CalendarioEditorialMkt, PublicacionesMkt, CuentasSocialesMkt  # noqa: F401
