-- Campo activo para planes de contenido — solo uno activo por marca
ALTER TABLE estrategia_mkt
  ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT false;
