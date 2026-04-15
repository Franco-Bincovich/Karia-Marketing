-- Agrega soporte de cuestionario y estado completado al onboarding
ALTER TABLE onboarding_mkt
  ADD COLUMN IF NOT EXISTS respuestas JSONB DEFAULT '{}',
  ADD COLUMN IF NOT EXISTS completado BOOLEAN DEFAULT false;
