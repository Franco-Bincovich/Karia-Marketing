-- Agrega variante C, CTAs y API key propia
ALTER TABLE contenido_mkt
  ADD COLUMN IF NOT EXISTS copy_c TEXT,
  ADD COLUMN IF NOT EXISTS hashtags_c TEXT,
  ADD COLUMN IF NOT EXISTS cta_a TEXT,
  ADD COLUMN IF NOT EXISTS cta_b TEXT,
  ADD COLUMN IF NOT EXISTS cta_c TEXT;

ALTER TABLE contenido_mkt
  DROP CONSTRAINT IF EXISTS contenido_mkt_variante_seleccionada_check;
ALTER TABLE contenido_mkt
  ADD CONSTRAINT contenido_mkt_variante_seleccionada_check
  CHECK (variante_seleccionada IN ('a','b','c'));

ALTER TABLE versiones_contenido_mkt
  ADD COLUMN IF NOT EXISTS copy_c TEXT;

ALTER TABLE clientes_mkt
  ADD COLUMN IF NOT EXISTS anthropic_api_key_encrypted TEXT;
