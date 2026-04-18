CREATE TABLE IF NOT EXISTS carrusel_slides_mkt (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  contenido_id UUID NOT NULL REFERENCES contenido_mkt(id) ON DELETE CASCADE,
  orden INTEGER NOT NULL,
  imagen_url TEXT,
  copy_slide TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_carrusel_contenido ON carrusel_slides_mkt(contenido_id);
