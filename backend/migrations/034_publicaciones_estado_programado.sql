ALTER TABLE publicaciones_mkt
DROP CONSTRAINT IF EXISTS publicaciones_mkt_estado_check;

ALTER TABLE publicaciones_mkt
ADD CONSTRAINT publicaciones_mkt_estado_check
CHECK (estado IN ('borrador', 'pendiente', 'programado', 'publicado', 'publicando', 'fallido', 'cancelado'));
