-- Módulo 8: Comunidad y Social Listening

CREATE TABLE mensajes_comunidad_mkt (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  marca_id UUID NOT NULL REFERENCES marcas_mkt(id) ON DELETE CASCADE,
  red_social TEXT NOT NULL,
  tipo TEXT CHECK (tipo IN ('comentario','dm','mencion','story_reply')) NOT NULL,
  autor_username TEXT,
  autor_id_externo TEXT,
  contenido TEXT NOT NULL,
  clasificacion TEXT CHECK (clasificacion IN ('consulta_comercial','consulta_tecnica','positivo','negativo','agresivo','spam','lead')) DEFAULT 'consulta_comercial',
  sentimiento TEXT CHECK (sentimiento IN ('positivo','negativo','neutro','mixto')) DEFAULT 'neutro',
  respuesta TEXT,
  respondido BOOLEAN DEFAULT false,
  escalado BOOLEAN DEFAULT false,
  motivo_escalado TEXT,
  es_lead BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  respondido_at TIMESTAMPTZ
);

CREATE TABLE config_comunidad_mkt (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  marca_id UUID NOT NULL REFERENCES marcas_mkt(id) ON DELETE CASCADE UNIQUE,
  criterios_escalado TEXT[],
  tiempo_respuesta_max INTEGER DEFAULT 120,
  responder_agresivos BOOLEAN DEFAULT false,
  responder_spam BOOLEAN DEFAULT false,
  modo TEXT CHECK (modo IN ('autopilot','copilot')) DEFAULT 'copilot',
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE menciones_mkt (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  marca_id UUID NOT NULL REFERENCES marcas_mkt(id) ON DELETE CASCADE,
  tipo TEXT CHECK (tipo IN ('marca','competidor','sector')) NOT NULL,
  fuente TEXT NOT NULL,
  url TEXT,
  autor TEXT,
  contenido TEXT NOT NULL,
  sentimiento TEXT CHECK (sentimiento IN ('positivo','negativo','neutro','mixto')) DEFAULT 'neutro',
  alcance_estimado INTEGER DEFAULT 0,
  urgente BOOLEAN DEFAULT false,
  procesado BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE config_listening_mkt (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  marca_id UUID NOT NULL REFERENCES marcas_mkt(id) ON DELETE CASCADE UNIQUE,
  terminos_marca TEXT[],
  terminos_competidores TEXT[],
  keywords_sector TEXT[],
  notificar_negativas BOOLEAN DEFAULT true,
  notificar_competidores BOOLEAN DEFAULT true,
  umbral_urgencia INTEGER DEFAULT 1000,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_mensajes_comunidad_marca ON mensajes_comunidad_mkt(marca_id);
CREATE INDEX idx_mensajes_no_respondidos ON mensajes_comunidad_mkt(respondido, marca_id);
CREATE INDEX idx_menciones_marca ON menciones_mkt(marca_id);
CREATE INDEX idx_menciones_urgentes ON menciones_mkt(urgente, procesado);
