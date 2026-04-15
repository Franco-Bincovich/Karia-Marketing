-- Score de sentimiento y flag de alerta en menciones
ALTER TABLE menciones_mkt
  ADD COLUMN IF NOT EXISTS score_sentimiento INTEGER DEFAULT 50,
  ADD COLUMN IF NOT EXISTS alerta_generada BOOLEAN DEFAULT false;
