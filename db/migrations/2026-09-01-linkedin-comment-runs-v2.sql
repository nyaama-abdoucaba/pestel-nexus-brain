BEGIN;

ALTER TABLE linkedin_comment_runs
  DROP CONSTRAINT IF EXISTS linkedin_comment_runs_status_chk,
  DROP CONSTRAINT IF EXISTS linkedin_comment_runs_ready_comment_chk,
  DROP CONSTRAINT IF EXISTS linkedin_comment_runs_diagnostics_array_chk,
  DROP CONSTRAINT IF EXISTS linkedin_comment_runs_diagnostics_object_chk;

UPDATE linkedin_comment_runs
SET status = CASE status
  WHEN 'ready_for_review' THEN 'draft'
  WHEN 'rejected' THEN 'skip'
  WHEN 'needs_human_review' THEN 'error'
  WHEN 'failed' THEN 'error'
  ELSE status
END
WHERE status IN ('ready_for_review', 'rejected', 'needs_human_review', 'failed');

UPDATE linkedin_comment_runs
SET diagnostics = jsonb_build_object(
  'reason_code', NULL,
  'reader_world', NULL,
  'post_type', NULL,
  'details', diagnostics
)
WHERE jsonb_typeof(diagnostics) = 'array';

ALTER TABLE linkedin_comment_runs
  ALTER COLUMN diagnostics SET DEFAULT '{}'::jsonb,
  ADD CONSTRAINT linkedin_comment_runs_status_chk CHECK (
    status IN ('draft', 'skip', 'error')
  ),
  ADD CONSTRAINT linkedin_comment_runs_ready_comment_chk CHECK (
    status <> 'draft' OR btrim(COALESCE(comment_text, '')) <> ''
  ),
  ADD CONSTRAINT linkedin_comment_runs_diagnostics_object_chk CHECK (
    jsonb_typeof(diagnostics) = 'object'
  );

COMMIT;
