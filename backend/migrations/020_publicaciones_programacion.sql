-- Agrega soporte de programación y tracking de posts/mes a publicaciones_mkt
ALTER TABLE publicaciones_mkt
  ADD COLUMN IF NOT EXISTS programado_para TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS zernio_post_id TEXT;
