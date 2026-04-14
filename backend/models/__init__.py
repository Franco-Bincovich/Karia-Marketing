"""Importa todos los modelos para que SQLAlchemy los registre correctamente."""

from models.cliente_models import ClienteMkt, MarcaMkt  # noqa: F401
from models.auth_models import UsuarioMkt, SesionMkt, UsuarioMarcaMkt  # noqa: F401
from models.permisos_models import PermisoMkt, FeatureFlagMkt, OnboardingMkt, AuditoriaMkt  # noqa: F401
from models.contacto_models import ContactoMkt  # noqa: F401
from models.contenido_models import ContenidoMkt, VersionesContenidoMkt, AprendizajeMkt, TemplatesMkt  # noqa: F401
from models.social_models import CalendarioEditorialMkt, PublicacionesMkt, CuentasSocialesMkt  # noqa: F401
from models.ads_models import CampanaAdsMkt, AdMkt, MetricasAdsMkt, UmbralesAdsMkt  # noqa: F401
from models.seo_models import KeywordMkt, AuditoriaSeoMkt, BriefSeoMkt, ConfigSeoMkt  # noqa: F401
from models.analytics_models import MetricasSocialesMkt, KpiClienteMkt, ReporteMkt, AlertaMkt, ConfigReportesMkt  # noqa: F401
from models.comunidad_models import MensajeComunidadMkt, ConfigComunidadMkt, MencionMkt, ConfigListeningMkt  # noqa: F401
from models.onboarding_models import MemoriaMarcaMkt, HistorialOnboardingMkt  # noqa: F401
