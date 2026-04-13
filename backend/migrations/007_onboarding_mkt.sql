CREATE TABLE IF NOT EXISTS onboarding_mkt (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  marca_id UUID NOT NULL REFERENCES marcas_mkt(id) ON DELETE CASCADE UNIQUE,
  paso_1_info_basica BOOLEAN DEFAULT false,
  paso_2_identidad_marca BOOLEAN DEFAULT false,
  paso_3_tono_voz BOOLEAN DEFAULT false,
  paso_4_audiencia BOOLEAN DEFAULT false,
  paso_5_competidores BOOLEAN DEFAULT false,
  paso_6_productos BOOLEAN DEFAULT false,
  paso_7_objetivos BOOLEAN DEFAULT false,
  paso_8_integraciones BOOLEAN DEFAULT false,
  paso_9_notificaciones BOOLEAN DEFAULT false,
  paso_10_subusuarios BOOLEAN DEFAULT false,
  completitud INTEGER DEFAULT 0,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
