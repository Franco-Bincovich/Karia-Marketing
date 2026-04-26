"""Importa todos los modelos para que SQLAlchemy los registre correctamente."""

from models.ads_models import AdMkt, CampanaAdsMkt, MetricasAdsMkt, UmbralesAdsMkt  # noqa: F401
from models.analytics_models import AlertaMkt, ConfigReportesMkt, KpiClienteMkt, MetricasSocialesMkt, ReporteMkt  # noqa: F401
from models.auth_models import SesionMkt, UsuarioMarcaMkt, UsuarioMkt  # noqa: F401
from models.cliente_models import ClienteMkt, MarcaMkt  # noqa: F401
from models.comunidad_models import ConfigComunidadMkt, ConfigListeningMkt, MencionMkt, MensajeComunidadMkt  # noqa: F401
from models.contacto_models import ContactoMkt  # noqa: F401
from models.contenido_models import AprendizajeMkt, ContenidoMkt, TemplatesMkt, VersionesContenidoMkt  # noqa: F401
from models.onboarding_models import HistorialOnboardingMkt, MemoriaMarcaMkt  # noqa: F401
from models.permisos_models import AuditoriaMkt, FeatureFlagMkt, OnboardingMkt, PermisoMkt  # noqa: F401
from models.seo_models import AuditoriaSeoMkt, BriefSeoMkt, ConfigSeoMkt, KeywordMkt  # noqa: F401
from models.social_models import CalendarioEditorialMkt, CuentasSocialesMkt, PublicacionesMkt  # noqa: F401
