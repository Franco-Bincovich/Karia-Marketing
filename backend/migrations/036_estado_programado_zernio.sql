-- Agrega estado 'programado_zernio' para distinguir posts que ya fueron enviados
-- a Zernio para programación interna vs. posts que NEXO aún debe enviar.
-- Previene que el scheduler re-publique posts que Zernio ya tiene en cola.

ALTER TABLE publicaciones_mkt
DROP CONSTRAINT IF EXISTS publicaciones_mkt_estado_check;

ALTER TABLE publicaciones_mkt
ADD CONSTRAINT publicaciones_mkt_estado_check
CHECK (estado IN ('borrador', 'programado', 'programado_zernio', 'publicando', 'publicado', 'fallido', 'cancelado'));

-- Migrar registros existentes: si tienen zernio_post_id y estado programado,
-- ya fueron enviados a Zernio
UPDATE publicaciones_mkt
SET estado = 'programado_zernio'
WHERE estado = 'programado'
AND zernio_post_id IS NOT NULL;
