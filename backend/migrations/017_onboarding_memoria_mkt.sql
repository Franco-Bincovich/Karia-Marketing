-- Módulo 9: Onboarding y Memoria de Marca

CREATE TABLE memoria_marca_mkt (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  marca_id UUID NOT NULL REFERENCES marcas_mkt(id) ON DELETE CASCADE UNIQUE,
  nombre_marca TEXT,
  industria TEXT,
  descripcion TEXT,
  propuesta_valor TEXT,
  productos_servicios JSONB,
  publico_objetivo TEXT,
  tono_voz TEXT CHECK (tono_voz IN ('profesional','cercano','inspirador','humoristico','informativo','urgente')) DEFAULT 'profesional',
  palabras_clave TEXT[],
  palabras_prohibidas TEXT[],
  colores_marca TEXT[],
  tipografia TEXT,
  ejemplos_contenido_aprobado TEXT[],
  competidores JSONB,
  diferenciadores TEXT[],
  sitio_web TEXT,
  preguntas_frecuentes JSONB,
  politica_respuestas TEXT,
  icp_descripcion TEXT,
  icp_cargo TEXT[],
  icp_industria TEXT[],
  icp_tamano_empresa TEXT,
  objetivos_periodo JSONB,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE historial_onboarding_mkt (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  marca_id UUID NOT NULL REFERENCES marcas_mkt(id) ON DELETE CASCADE,
  paso INTEGER NOT NULL,
  campo TEXT NOT NULL,
  valor_anterior TEXT,
  valor_nuevo TEXT,
  modificado_por UUID REFERENCES usuarios_mkt(id),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_memoria_marca ON memoria_marca_mkt(marca_id);
CREATE INDEX idx_historial_onboarding ON historial_onboarding_mkt(marca_id);
