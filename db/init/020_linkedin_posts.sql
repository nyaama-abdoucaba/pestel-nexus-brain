BEGIN;

CREATE TABLE linkedin_posts (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  linkedin_target_id uuid NOT NULL
    REFERENCES linkedin_targets(id) ON DELETE RESTRICT,
  url text NOT NULL UNIQUE,
  text text NOT NULL,
  posted_at timestamptz,
  observed_at timestamptz NOT NULL DEFAULT now(),
  status text NOT NULL DEFAULT 'observed',
  raw_payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT linkedin_posts_url_chk CHECK (
    url ~ '^https://www\.linkedin\.com/.+'
  ),
  CONSTRAINT linkedin_posts_text_chk CHECK (btrim(text) <> ''),
  CONSTRAINT linkedin_posts_status_chk CHECK (
    status IN ('observed', 'selected', 'commented', 'skipped')
  ),
  CONSTRAINT linkedin_posts_raw_payload_object_chk CHECK (
    jsonb_typeof(raw_payload) = 'object'
  )
);

CREATE INDEX linkedin_posts_target_posted_idx
  ON linkedin_posts(linkedin_target_id, posted_at DESC NULLS LAST);

CREATE INDEX linkedin_posts_status_idx
  ON linkedin_posts(status);

CREATE INDEX linkedin_posts_observed_idx
  ON linkedin_posts(observed_at DESC);

CREATE TRIGGER linkedin_posts_touch_updated_at
BEFORE UPDATE ON linkedin_posts
FOR EACH ROW
EXECUTE FUNCTION touch_updated_at();

COMMIT;
