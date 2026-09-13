BEGIN;

CREATE TABLE linkedin_comment_runs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  linkedin_post_id uuid NOT NULL REFERENCES linkedin_posts(id) ON DELETE CASCADE,
  status text NOT NULL,
  source_language text,
  comment_text text,
  analysis_payload jsonb,
  revisions_payload jsonb NOT NULL DEFAULT '[]'::jsonb,
  diagnostics jsonb NOT NULL DEFAULT '{}'::jsonb,
  model_name text NOT NULL,
  prompt_version text NOT NULL,
  content_hash text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT linkedin_comment_runs_status_chk CHECK (
    status IN ('draft', 'skip', 'error')
  ),
  CONSTRAINT linkedin_comment_runs_source_language_chk CHECK (
    source_language IS NULL OR source_language IN ('fr', 'en')
  ),
  CONSTRAINT linkedin_comment_runs_ready_comment_chk CHECK (
    status <> 'draft' OR btrim(COALESCE(comment_text, '')) <> ''
  ),
  CONSTRAINT linkedin_comment_runs_analysis_object_chk CHECK (
    analysis_payload IS NULL OR jsonb_typeof(analysis_payload) = 'object'
  ),
  CONSTRAINT linkedin_comment_runs_revisions_array_chk CHECK (
    jsonb_typeof(revisions_payload) = 'array'
  ),
  CONSTRAINT linkedin_comment_runs_diagnostics_object_chk CHECK (
    jsonb_typeof(diagnostics) = 'object'
  ),
  CONSTRAINT linkedin_comment_runs_content_hash_chk CHECK (
    content_hash ~ '^[0-9a-f]{64}$'
  )
);

CREATE INDEX linkedin_comment_runs_post_created_idx
  ON linkedin_comment_runs(linkedin_post_id, created_at DESC);

CREATE INDEX linkedin_comment_runs_status_created_idx
  ON linkedin_comment_runs(status, created_at DESC);

CREATE INDEX linkedin_comment_runs_post_hash_status_idx
  ON linkedin_comment_runs(linkedin_post_id, content_hash, status);

COMMIT;
