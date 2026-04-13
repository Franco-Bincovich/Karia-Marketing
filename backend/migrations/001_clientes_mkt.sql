CREATE TABLE IF NOT EXISTS clientes_mkt (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  nombre TEXT NOT NULL,
  email_admin TEXT UNIQUE NOT NULL,
  pais TEXT DEFAULT 'AR',
  activo BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
