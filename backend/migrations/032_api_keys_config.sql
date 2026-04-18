CREATE TABLE IF NOT EXISTS api_keys_config_mkt (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  cliente_id UUID NOT NULL REFERENCES clientes_mkt(id) ON DELETE CASCADE,
  servicio TEXT NOT NULL,
  api_key_encrypted TEXT,
  configurada BOOLEAN DEFAULT false,
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(cliente_id, servicio)
);
