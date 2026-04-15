CREATE TABLE IF NOT EXISTS automatizaciones_mkt (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  marca_id UUID NOT NULL REFERENCES marcas_mkt(id) ON DELETE CASCADE,
  nombre TEXT NOT NULL,
  descripcion TEXT,
  tipo TEXT CHECK (tipo IN ('vencimientos','listening','reporte','publicacion','orquestador')) NOT NULL,
  activa BOOLEAN DEFAULT true,
  ultima_ejecucion TIMESTAMPTZ,
  proxima_ejecucion TIMESTAMPTZ,
  intervalo_horas INTEGER NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(marca_id, tipo)
);

CREATE INDEX IF NOT EXISTS idx_automatizaciones_marca ON automatizaciones_mkt(marca_id);
