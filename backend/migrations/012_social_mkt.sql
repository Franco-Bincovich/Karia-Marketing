CREATE TABLE IF NOT EXISTS calendario_editorial_mkt (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  marca_id UUID NOT NULL REFERENCES marcas_mkt(id) ON DELETE CASCADE,
  cliente_id UUID NOT NULL REFERENCES clientes_mkt(id) ON DELETE CASCADE,
  contenido_id UUID REFERENCES contenido_mkt(id) ON DELETE SET NULL,
  titulo TEXT NOT NULL,
  descripcion TEXT,
  red_social TEXT CHECK (red_social IN ('instagram','facebook','linkedin','tiktok','twitter','youtube')) NOT NULL,
  formato TEXT NOT NULL,
  fecha_programada TIMESTAMPTZ NOT NULL,
  estado TEXT CHECK (estado IN ('programado','publicado','fallido','cancelado')) DEFAULT 'programado',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS publicaciones_mkt (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  marca_id UUID NOT NULL REFERENCES marcas_mkt(id) ON DELETE CASCADE,
  calendario_id UUID REFERENCES calendario_editorial_mkt(id) ON DELETE SET NULL,
  contenido_id UUID REFERENCES contenido_mkt(id) ON DELETE SET NULL,
  red_social TEXT NOT NULL,
  post_id_externo TEXT,
  url_publicacion TEXT,
  copy_publicado TEXT,
  imagen_url TEXT,
  estado TEXT CHECK (estado IN ('publicado','fallido','reintentando')) DEFAULT 'publicado',
  intentos INTEGER DEFAULT 1,
  error_detalle TEXT,
  likes_2hs INTEGER DEFAULT 0,
  comentarios_2hs INTEGER DEFAULT 0,
  alcance_2hs INTEGER DEFAULT 0,
  engagement_bajo BOOLEAN DEFAULT false,
  publicado_at TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS cuentas_sociales_mkt (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  marca_id UUID NOT NULL REFERENCES marcas_mkt(id) ON DELETE CASCADE,
  red_social TEXT CHECK (red_social IN ('instagram','facebook','linkedin','tiktok','twitter','youtube')) NOT NULL,
  nombre_cuenta TEXT NOT NULL,
  account_id_externo TEXT,
  access_token_encrypted TEXT,
  token_expires_at TIMESTAMPTZ,
  activa BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(marca_id, red_social)
);

CREATE INDEX IF NOT EXISTS idx_calendario_marca    ON calendario_editorial_mkt(marca_id);
CREATE INDEX IF NOT EXISTS idx_calendario_fecha    ON calendario_editorial_mkt(fecha_programada);
CREATE INDEX IF NOT EXISTS idx_publicaciones_marca ON publicaciones_mkt(marca_id);
CREATE INDEX IF NOT EXISTS idx_cuentas_sociales_marca ON cuentas_sociales_mkt(marca_id);
