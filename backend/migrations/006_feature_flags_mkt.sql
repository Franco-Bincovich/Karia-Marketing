CREATE TABLE IF NOT EXISTS feature_flags_mkt (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  cliente_id UUID NOT NULL REFERENCES clientes_mkt(id) ON DELETE CASCADE,
  marca_id UUID REFERENCES marcas_mkt(id) ON DELETE CASCADE,
  feature TEXT NOT NULL,
  habilitado BOOLEAN DEFAULT true,
  modo TEXT CHECK (modo IN ('ia','manual','autopilot','copilot')) DEFAULT 'copilot',
  UNIQUE(cliente_id, marca_id, feature)
);
