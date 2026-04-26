"""Cliente Anthropic — facade que re-exporta desde submódulos.

Todos los callers existentes importan de este archivo.
La implementación real está en integrations/claude/*.
"""

# Base: cliente, constantes, parsers
# Agentes: traducción visual
from integrations.claude.agentes import (  # noqa: F401
    traducir_concepto_a_prompt_visual,
)
from integrations.claude.base import (  # noqa: F401
    _SEARCH_MODEL,
    _WEB_SEARCH_TOOL,
    _get_client,
    _parse_json_array,
    _parse_json_object,
)

# Contenido: generación de copies y prospección
from integrations.claude.contenido import (  # noqa: F401
    buscar_contactos_ia,
    generar_contenido_ia,
)

# Onboarding: sugerencias y autocompletado
from integrations.claude.onboarding import (  # noqa: F401
    autocompletar_perfil_marca,
    sugerir_respuesta_onboarding,
)
