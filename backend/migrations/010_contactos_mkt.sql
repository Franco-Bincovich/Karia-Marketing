CREATE TABLE IF NOT EXISTS contactos_mkt (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  marca_id UUID NOT NULL REFERENCES marcas_mkt(id) ON DELETE CASCADE,
  cliente_id UUID NOT NULL REFERENCES clientes_mkt(id) ON DELETE CASCADE,
  nombre TEXT,
  empresa TEXT NOT NULL,
  cargo TEXT,
  email_empresarial TEXT,
  email_personal TEXT,
  telefono_empresa TEXT,
  telefono_personal TEXT,
  linkedin_url TEXT,
  confianza INTEGER DEFAULT 0,
  origen TEXT CHECK (origen IN ('ai','manual','apollo','apify')) DEFAULT 'ai',
  score INTEGER DEFAULT 0,
  estado TEXT CHECK (estado IN ('nuevo','calificado','contactado','respondio','archivado')) DEFAULT 'nuevo',
  notas TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_contactos_mkt_marca ON contactos_mkt(marca_id);
CREATE INDEX IF NOT EXISTS idx_contactos_mkt_cliente ON contactos_mkt(cliente_id);
CREATE INDEX IF NOT EXISTS idx_contactos_mkt_estado ON contactos_mkt(estado);
