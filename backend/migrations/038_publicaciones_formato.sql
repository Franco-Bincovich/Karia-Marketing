-- Agrega columna formato a publicaciones_mkt para distinguir post/story/reel/carrusel.
-- Default 'post' para no romper registros existentes.

ALTER TABLE publicaciones_mkt
ADD COLUMN IF NOT EXISTS formato TEXT DEFAULT 'post';
