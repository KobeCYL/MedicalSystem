CREATE TABLE IF NOT EXISTS public.queries (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  timestamp timestamptz NOT NULL DEFAULT now(),
  user_id text,
  symptom text NOT NULL,
  patient_info jsonb,
  status text,
  disease_name text,
  advice jsonb,
  urgency text,
  server_duration_ms int,
  total_duration_ms int,
  supplementary_info jsonb,
  model text,
  source_channel text
);

CREATE INDEX IF NOT EXISTS idx_queries_timestamp ON public.queries (timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_queries_status ON public.queries (status);
CREATE INDEX IF NOT EXISTS idx_queries_user ON public.queries (user_id);

CREATE TABLE IF NOT EXISTS public.security_events (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  query_id uuid REFERENCES public.queries(id) ON DELETE CASCADE,
  risk_score int,
  high_risk_matches jsonb,
  medium_risk_matches jsonb,
  is_medical boolean,
  llm_confidence int
);

CREATE INDEX IF NOT EXISTS idx_security_query ON public.security_events (query_id);
