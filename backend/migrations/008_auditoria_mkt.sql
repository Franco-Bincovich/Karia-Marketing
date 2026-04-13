CREATE TABLE IF NOT EXISTS auditoria_mkt (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  usuario_id UUID REFERENCES usuarios_mkt(id),
  cliente_id UUID REFERENCES clientes_mkt(id),
  marca_id UUID REFERENCES marcas_mkt(id),
  accion TEXT NOT NULL,
  modulo TEXT NOT NULL,
  recurso_id TEXT,
  detalle JSONB,
  ip TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
