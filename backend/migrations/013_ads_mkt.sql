-- Módulo 5: Ads (Meta Ads + Google Ads)

CREATE TABLE campanas_ads_mkt (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  marca_id UUID NOT NULL REFERENCES marcas_mkt(id) ON DELETE CASCADE,
  cliente_id UUID NOT NULL REFERENCES clientes_mkt(id) ON DELETE CASCADE,
  nombre TEXT NOT NULL,
  plataforma TEXT CHECK (plataforma IN ('meta','google')) NOT NULL,
  objetivo TEXT,
  presupuesto_diario DECIMAL(10,2) NOT NULL,
  presupuesto_mensual DECIMAL(10,2),
  campaign_id_externo TEXT,
  estado TEXT CHECK (estado IN ('borrador','pendiente_aprobacion','activa','pausada','finalizada')) DEFAULT 'borrador',
  aprobada_por UUID REFERENCES usuarios_mkt(id),
  aprobada_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE ads_mkt (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  campana_id UUID NOT NULL REFERENCES campanas_ads_mkt(id) ON DELETE CASCADE,
  marca_id UUID NOT NULL REFERENCES marcas_mkt(id) ON DELETE CASCADE,
  nombre TEXT NOT NULL,
  copy_titulo TEXT,
  copy_descripcion TEXT,
  imagen_url TEXT,
  ad_id_externo TEXT,
  variante TEXT CHECK (variante IN ('a','b')) DEFAULT 'a',
  estado TEXT CHECK (estado IN ('activo','pausado','archivado')) DEFAULT 'activo',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE metricas_ads_mkt (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  campana_id UUID NOT NULL REFERENCES campanas_ads_mkt(id) ON DELETE CASCADE,
  ad_id UUID REFERENCES ads_mkt(id) ON DELETE CASCADE,
  marca_id UUID NOT NULL REFERENCES marcas_mkt(id) ON DELETE CASCADE,
  fecha DATE NOT NULL,
  impresiones INTEGER DEFAULT 0,
  clicks INTEGER DEFAULT 0,
  conversiones INTEGER DEFAULT 0,
  gasto DECIMAL(10,2) DEFAULT 0,
  roas DECIMAL(6,2) DEFAULT 0,
  cpa DECIMAL(10,2) DEFAULT 0,
  ctr DECIMAL(5,4) DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(campana_id, ad_id, fecha)
);

CREATE TABLE umbrales_ads_mkt (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  marca_id UUID NOT NULL REFERENCES marcas_mkt(id) ON DELETE CASCADE UNIQUE,
  cpa_maximo DECIMAL(10,2) DEFAULT 40.00,
  roas_minimo DECIMAL(6,2) DEFAULT 2.50,
  gasto_diario_maximo DECIMAL(10,2) DEFAULT 500.00,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_campanas_marca ON campanas_ads_mkt(marca_id);
CREATE INDEX idx_campanas_estado ON campanas_ads_mkt(estado);
CREATE INDEX idx_ads_campana ON ads_mkt(campana_id);
CREATE INDEX idx_metricas_campana ON metricas_ads_mkt(campana_id);
CREATE INDEX idx_metricas_fecha ON metricas_ads_mkt(fecha);
