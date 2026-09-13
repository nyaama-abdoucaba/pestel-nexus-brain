BEGIN;

ALTER TABLE linkedin_targets
  DROP CONSTRAINT IF EXISTS linkedin_targets_url_chk,
  ADD CONSTRAINT linkedin_targets_url_chk CHECK (
    linkedin_url ~ '^https://(www\.)?linkedin\.com/(in|company|school)/[^/?#]+/?$'
  );

COMMIT;
