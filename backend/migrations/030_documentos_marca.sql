CREATE TABLE IF NOT EXISTS documentos_marca_mkt (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  marca_id UUID NOT NULL REFERENCES marcas_mkt(id) ON DELETE CASCADE,
  nombre_archivo TEXT NOT NULL,
  tipo TEXT NOT NULL,
  url_storage TEXT,
  texto_extraido TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_documentos_marca ON documentos_marca_mkt(marca_id);
