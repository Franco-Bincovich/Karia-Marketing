-- Módulo 7: Analytics y Reporting

CREATE TABLE metricas_sociales_mkt (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  marca_id UUID NOT NULL REFERENCES marcas_mkt(id) ON DELETE CASCADE,
  red_social TEXT NOT NULL,
  fecha DATE NOT NULL,
  alcance INTEGER DEFAULT 0,
  impresiones INTEGER DEFAULT 0,
  engagement INTEGER DEFAULT 0,
  engagement_rate DECIMAL(5,4) DEFAULT 0,
  nuevos_seguidores INTEGER DEFAULT 0,
  clicks INTEGER DEFAULT 0,
  reproducciones_video INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(marca_id, red_social, fecha)
);

CREATE TABLE kpis_cliente_mkt (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  marca_id UUID NOT NULL REFERENCES marcas_mkt(id) ON DELETE CASCADE,
  kpi TEXT NOT NULL,
  activo BOOLEAN DEFAULT true,
  valor_actual DECIMAL(12,2) DEFAULT 0,
  valor_objetivo DECIMAL(12,2),
  periodo TEXT CHECK (periodo IN ('diario','semanal','mensual')) DEFAULT 'mensual',
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(marca_id, kpi)
);

CREATE TABLE reportes_mkt (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  marca_id UUID NOT NULL REFERENCES marcas_mkt(id) ON DELETE CASCADE,
  tipo TEXT CHECK (tipo IN ('diario','semanal','mensual')) NOT NULL,
  periodo_inicio DATE NOT NULL,
  periodo_fin DATE NOT NULL,
  contenido JSONB NOT NULL,
  formato TEXT CHECK (formato IN ('pdf','whatsapp','email','panel')) NOT NULL,
  enviado BOOLEAN DEFAULT false,
  enviado_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE alertas_mkt (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  marca_id UUID NOT NULL REFERENCES marcas_mkt(id) ON DELETE CASCADE,
  tipo TEXT NOT NULL,
  canal TEXT CHECK (canal IN ('email','whatsapp','panel')) DEFAULT 'panel',
  mensaje TEXT NOT NULL,
  datos JSONB,
  leida BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE config_reportes_mkt (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  marca_id UUID NOT NULL REFERENCES marcas_mkt(id) ON DELETE CASCADE UNIQUE,
  frecuencia TEXT CHECK (frecuencia IN ('diario','semanal','mensual')) DEFAULT 'semanal',
  formatos TEXT[] DEFAULT ARRAY['panel'],
  canal_notificacion TEXT CHECK (canal_notificacion IN ('email','whatsapp','panel','todos')) DEFAULT 'panel',
  email_reporte TEXT,
  whatsapp_reporte TEXT,
  incluir_comparacion BOOLEAN DEFAULT true,
  periodo_comparacion TEXT CHECK (periodo_comparacion IN ('semana_anterior','mes_anterior','mismo_periodo_anterior')) DEFAULT 'semana_anterior',
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_metricas_sociales_marca ON metricas_sociales_mkt(marca_id);
CREATE INDEX idx_metricas_sociales_fecha ON metricas_sociales_mkt(fecha);
CREATE INDEX idx_kpis_marca ON kpis_cliente_mkt(marca_id);
CREATE INDEX idx_reportes_marca ON reportes_mkt(marca_id);
CREATE INDEX idx_alertas_marca ON alertas_mkt(marca_id);
