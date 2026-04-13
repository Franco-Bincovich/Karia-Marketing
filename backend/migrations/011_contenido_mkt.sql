CREATE TABLE IF NOT EXISTS contenido_mkt (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  marca_id UUID NOT NULL REFERENCES marcas_mkt(id) ON DELETE CASCADE,
  cliente_id UUID NOT NULL REFERENCES clientes_mkt(id) ON DELETE CASCADE,
  red_social TEXT CHECK (red_social IN ('instagram','facebook','linkedin','tiktok','twitter','youtube','email','blog')) NOT NULL,
  formato TEXT CHECK (formato IN ('post','story','reel','carrusel','articulo','script','email')) NOT NULL,
  objetivo TEXT,
  tono TEXT,
  tema TEXT,
  copy_a TEXT,
  copy_b TEXT,
  hashtags_a TEXT,
  hashtags_b TEXT,
  variante_seleccionada TEXT CHECK (variante_seleccionada IN ('a','b')) DEFAULT NULL,
  estado TEXT CHECK (estado IN ('borrador','pendiente_aprobacion','aprobado','rechazado','publicado')) DEFAULT 'borrador',
  modo TEXT CHECK (modo IN ('autopilot','copilot')) DEFAULT 'copilot',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS versiones_contenido_mkt (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  contenido_id UUID NOT NULL REFERENCES contenido_mkt(id) ON DELETE CASCADE,
  version INTEGER NOT NULL DEFAULT 1,
  copy_a TEXT,
  copy_b TEXT,
  motivo_rechazo TEXT,
  creado_por TEXT CHECK (creado_por IN ('ia','humano')) DEFAULT 'ia',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS aprendizaje_mkt (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  marca_id UUID NOT NULL REFERENCES marcas_mkt(id) ON DELETE CASCADE,
  contenido_id UUID REFERENCES contenido_mkt(id),
  tipo TEXT CHECK (tipo IN ('aprobacion','rechazo','edicion')) NOT NULL,
  red_social TEXT,
  formato TEXT,
  tono TEXT,
  comentario TEXT,
  copy_original TEXT,
  copy_final TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS templates_mkt (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  marca_id UUID NOT NULL REFERENCES marcas_mkt(id) ON DELETE CASCADE,
  nombre TEXT NOT NULL,
  red_social TEXT NOT NULL,
  formato TEXT NOT NULL,
  copy TEXT NOT NULL,
  hashtags TEXT,
  tono TEXT,
  objetivo TEXT,
  usos INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_contenido_mkt_marca   ON contenido_mkt(marca_id);
CREATE INDEX IF NOT EXISTS idx_contenido_mkt_estado  ON contenido_mkt(estado);
CREATE INDEX IF NOT EXISTS idx_versiones_contenido   ON versiones_contenido_mkt(contenido_id);
CREATE INDEX IF NOT EXISTS idx_aprendizaje_marca     ON aprendizaje_mkt(marca_id);
CREATE INDEX IF NOT EXISTS idx_templates_marca       ON templates_mkt(marca_id);
