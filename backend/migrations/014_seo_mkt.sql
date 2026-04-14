-- Módulo 6: SEO (Keywords, Auditoría, Briefs, Configuración)

CREATE TABLE keywords_mkt (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  marca_id UUID NOT NULL REFERENCES marcas_mkt(id) ON DELETE CASCADE,
  keyword TEXT NOT NULL,
  volumen_mensual INTEGER DEFAULT 0,
  dificultad INTEGER DEFAULT 0,
  intencion TEXT CHECK (intencion IN ('informacional','navegacional','transaccional','comercial')) DEFAULT 'informacional',
  posicion_actual INTEGER,
  posicion_anterior INTEGER,
  clicks_organicos INTEGER DEFAULT 0,
  impresiones INTEGER DEFAULT 0,
  ctr DECIMAL(5,4) DEFAULT 0,
  url_objetivo TEXT,
  estado TEXT CHECK (estado IN ('monitoreando','oportunidad','ranking','perdida')) DEFAULT 'monitoreando',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(marca_id, keyword)
);

CREATE TABLE auditoria_seo_mkt (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  marca_id UUID NOT NULL REFERENCES marcas_mkt(id) ON DELETE CASCADE,
  url TEXT NOT NULL,
  tipo TEXT CHECK (tipo IN ('velocidad','meta','links','schema','mobile','core_web_vitals')) NOT NULL,
  severidad TEXT CHECK (severidad IN ('critico','alto','medio','bajo')) NOT NULL,
  descripcion TEXT NOT NULL,
  recomendacion TEXT NOT NULL,
  implementado BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE briefs_seo_mkt (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  marca_id UUID NOT NULL REFERENCES marcas_mkt(id) ON DELETE CASCADE,
  keyword_principal TEXT NOT NULL,
  keywords_secundarias TEXT,
  intencion_busqueda TEXT,
  estructura_sugerida TEXT,
  longitud_minima INTEGER DEFAULT 800,
  competidores_url TEXT,
  meta_title TEXT,
  meta_description TEXT,
  usado BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE config_seo_mkt (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  marca_id UUID NOT NULL REFERENCES marcas_mkt(id) ON DELETE CASCADE UNIQUE,
  sitio_web TEXT,
  frecuencia_reporte TEXT CHECK (frecuencia_reporte IN ('semanal','quincenal','mensual')) DEFAULT 'semanal',
  semrush_proyecto_id TEXT,
  search_console_conectado BOOLEAN DEFAULT false,
  competidores TEXT,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_keywords_marca ON keywords_mkt(marca_id);
CREATE INDEX idx_keywords_estado ON keywords_mkt(estado);
CREATE INDEX idx_auditoria_seo_marca ON auditoria_seo_mkt(marca_id);
CREATE INDEX idx_briefs_seo_marca ON briefs_seo_mkt(marca_id);
