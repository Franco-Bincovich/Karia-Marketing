CREATE TABLE IF NOT EXISTS permisos_mkt (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  usuario_id UUID NOT NULL REFERENCES usuarios_mkt(id) ON DELETE CASCADE,
  marca_id UUID NOT NULL REFERENCES marcas_mkt(id) ON DELETE CASCADE,
  modulo TEXT NOT NULL,
  accion TEXT NOT NULL,
  permitido BOOLEAN DEFAULT true,
  UNIQUE(usuario_id, marca_id, modulo, accion)
);
