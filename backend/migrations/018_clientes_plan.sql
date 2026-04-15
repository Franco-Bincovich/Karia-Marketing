-- Agrega campo plan a clientes_mkt
ALTER TABLE clientes_mkt
  ADD COLUMN IF NOT EXISTS plan TEXT NOT NULL DEFAULT 'Basic';
