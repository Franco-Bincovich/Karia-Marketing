CREATE TABLE IF NOT EXISTS estrategia_mkt (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  marca_id UUID NOT NULL REFERENCES marcas_mkt(id) ON DELETE CASCADE,
  tipo TEXT CHECK (tipo IN ('analisis','plan','sugerencia')) NOT NULL,
  contenido JSONB NOT NULL,
  periodo TEXT,
  implementada BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_estrategia_marca ON estrategia_mkt(marca_id);
