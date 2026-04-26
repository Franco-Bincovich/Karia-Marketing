-- Defensa en profundidad: previene a nivel DB que dos registros compartan
-- el mismo zernio_post_id, evitando duplicados aunque el scheduler falle.

ALTER TABLE publicaciones_mkt
ADD CONSTRAINT unique_zernio_post_id UNIQUE (zernio_post_id);
