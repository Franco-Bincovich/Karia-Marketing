-- Tabla de imágenes generadas con IA
CREATE TABLE IF NOT EXISTS imagenes_mkt (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  marca_id UUID NOT NULL REFERENCES marcas_mkt(id) ON DELETE CASCADE,
  contenido_id UUID REFERENCES contenido_mkt(id) ON DELETE SET NULL,
  prompt TEXT NOT NULL,
  imagen_url TEXT NOT NULL,
  tamano TEXT DEFAULT '1024x1024',
  estilo TEXT DEFAULT 'vivid',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_imagenes_marca ON imagenes_mkt(marca_id);

-- API key de OpenAI propia para Premium
ALTER TABLE clientes_mkt
  ADD COLUMN IF NOT EXISTS openai_api_key_encrypted TEXT;

-- Imagen asociada a contenido
ALTER TABLE contenido_mkt
  ADD COLUMN IF NOT EXISTS imagen_url TEXT;
