BEGIN;

-- Le runtime est l'unique propriétaire de l'historique de traitement.
-- L'empreinte fige le contenu traité pour que n8n relance seulement un post
-- dont le contenu a réellement changé.
ALTER TABLE linkedin_comment_runs
  ADD COLUMN IF NOT EXISTS content_hash text;

UPDATE linkedin_comment_runs r
SET content_hash = p.content_hash
FROM linkedin_posts p
WHERE p.id = r.linkedin_post_id
  AND r.content_hash IS NULL;

ALTER TABLE linkedin_comment_runs
  ALTER COLUMN content_hash SET NOT NULL;

ALTER TABLE linkedin_comment_runs
  DROP CONSTRAINT IF EXISTS linkedin_comment_runs_content_hash_chk,
  ADD CONSTRAINT linkedin_comment_runs_content_hash_chk CHECK (
    content_hash ~ '^[0-9a-f]{64}$'
  );

CREATE INDEX IF NOT EXISTS linkedin_comment_runs_post_hash_status_idx
  ON linkedin_comment_runs(linkedin_post_id, content_hash, status);

COMMIT;
