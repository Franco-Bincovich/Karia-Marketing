-- Asegura que la columna formato existe en publicaciones_mkt y rellena los nulos.
-- 038 agrega la columna con DEFAULT 'post' para filas nuevas, pero no actualiza
-- filas preexistentes que quedaron en null. Este script los cubre.

ALTER TABLE publicaciones_mkt
    ADD COLUMN IF NOT EXISTS formato TEXT DEFAULT 'post';

UPDATE publicaciones_mkt
    SET formato = 'post'
    WHERE formato IS NULL;
