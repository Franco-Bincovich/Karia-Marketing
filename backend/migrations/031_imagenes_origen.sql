-- Columna origen para distinguir imágenes generadas por IA vs subidas manualmente
ALTER TABLE imagenes_mkt
  ADD COLUMN IF NOT EXISTS origen TEXT DEFAULT 'ia',
  ALTER COLUMN prompt DROP NOT NULL;
