CREATE TABLE IF NOT EXISTS usuarios_marcas_mkt (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  usuario_id UUID NOT NULL REFERENCES usuarios_mkt(id) ON DELETE CASCADE,
  marca_id UUID NOT NULL REFERENCES marcas_mkt(id) ON DELETE CASCADE,
  UNIQUE(usuario_id, marca_id)
);
