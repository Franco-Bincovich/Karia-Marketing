CREATE TABLE IF NOT EXISTS marcas_mkt (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  cliente_id UUID NOT NULL REFERENCES clientes_mkt(id) ON DELETE CASCADE,
  nombre TEXT NOT NULL,
  industria TEXT,
  descripcion TEXT,
  sitio_web TEXT,
  activa BOOLEAN DEFAULT true,
  onboarding_completitud INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
