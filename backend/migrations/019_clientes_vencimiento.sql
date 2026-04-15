-- Agrega campos de vencimiento y renovación a clientes_mkt
ALTER TABLE clientes_mkt
  ADD COLUMN IF NOT EXISTS fecha_vencimiento TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS fecha_ultimo_pago TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS notificacion_enviada BOOLEAN DEFAULT false;

-- Inicializa fecha_vencimiento para clientes existentes (created_at + 30 días)
UPDATE clientes_mkt
SET fecha_vencimiento = created_at + INTERVAL '30 days'
WHERE fecha_vencimiento IS NULL;

-- Hace NOT NULL después de llenar los existentes
ALTER TABLE clientes_mkt
  ALTER COLUMN fecha_vencimiento SET NOT NULL;
