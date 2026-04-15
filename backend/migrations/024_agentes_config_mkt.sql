CREATE TABLE IF NOT EXISTS agentes_config_mkt (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  marca_id UUID NOT NULL REFERENCES marcas_mkt(id) ON DELETE CASCADE,
  agente_nombre TEXT NOT NULL,
  activo BOOLEAN DEFAULT true,
  modo TEXT CHECK (modo IN ('copilot','autopilot')) DEFAULT 'copilot',
  system_prompt_custom TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(marca_id, agente_nombre)
);

CREATE INDEX IF NOT EXISTS idx_agentes_config_marca ON agentes_config_mkt(marca_id);
