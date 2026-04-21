-- Campos nuevos para onboarding expandido (15 obligatorias + ~20 opcionales)
-- No rompe datos existentes: todos nullable con defaults

ALTER TABLE memoria_marca_mkt ADD COLUMN IF NOT EXISTS ciudad_zona TEXT;
ALTER TABLE memoria_marca_mkt ADD COLUMN IF NOT EXISTS dolor_cliente TEXT;
ALTER TABLE memoria_marca_mkt ADD COLUMN IF NOT EXISTS cta_principal TEXT;
ALTER TABLE memoria_marca_mkt ADD COLUMN IF NOT EXISTS frecuencia_publicacion TEXT;
ALTER TABLE memoria_marca_mkt ADD COLUMN IF NOT EXISTS aprobacion_contenido TEXT;
ALTER TABLE memoria_marca_mkt ADD COLUMN IF NOT EXISTS redes_activas TEXT[] DEFAULT '{}';
ALTER TABLE memoria_marca_mkt ADD COLUMN IF NOT EXISTS adjetivos_marca TEXT[] DEFAULT '{}';
ALTER TABLE memoria_marca_mkt ADD COLUMN IF NOT EXISTS ventaja_competitiva TEXT;
ALTER TABLE memoria_marca_mkt ADD COLUMN IF NOT EXISTS testimonios_resultados TEXT;
ALTER TABLE memoria_marca_mkt ADD COLUMN IF NOT EXISTS temporada_alta_baja TEXT;
ALTER TABLE memoria_marca_mkt ADD COLUMN IF NOT EXISTS fechas_especiales TEXT;
ALTER TABLE memoria_marca_mkt ADD COLUMN IF NOT EXISTS tiene_fotos_propias TEXT;
ALTER TABLE memoria_marca_mkt ADD COLUMN IF NOT EXISTS preferencia_imagenes TEXT;
ALTER TABLE memoria_marca_mkt ADD COLUMN IF NOT EXISTS personalidad_marca Text;
ALTER TABLE memoria_marca_mkt ADD COLUMN IF NOT EXISTS marcas_referencia TEXT;
ALTER TABLE memoria_marca_mkt ADD COLUMN IF NOT EXISTS estetica_visual TEXT;
