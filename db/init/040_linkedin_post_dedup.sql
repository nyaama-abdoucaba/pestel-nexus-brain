BEGIN;

CREATE OR REPLACE FUNCTION normalize_whitespace(input_text text)
RETURNS text
LANGUAGE sql
IMMUTABLE
AS $$
  SELECT NULLIF(regexp_replace(btrim(COALESCE(input_text, '')), '\s+', ' ', 'g'), '');
$$;

CREATE OR REPLACE FUNCTION canonicalize_linkedin_post_url(input_url text)
RETURNS text
LANGUAGE sql
IMMUTABLE
AS $$
  SELECT CASE
    WHEN NULLIF(btrim(COALESCE(input_url, '')), '') IS NULL THEN NULL
    ELSE regexp_replace(
      regexp_replace(
        regexp_replace(btrim(input_url), '[?#].*$', ''),
        '/+$',
        ''
      ),
      '^http://',
      'https://'
    )
  END;
$$;

CREATE OR REPLACE FUNCTION extract_linkedin_post_stable_id(input_url text)
RETURNS text
LANGUAGE sql
IMMUTABLE
AS $$
  SELECT COALESCE(
    substring(canonicalize_linkedin_post_url(input_url) FROM '(?:activity|ugcPost)-([0-9]+)'),
    substring(canonicalize_linkedin_post_url(input_url) FROM 'urn:li:(?:activity|ugcPost):([0-9]+)')
  );
$$;

CREATE OR REPLACE FUNCTION build_linkedin_post_content_hash(
  post_text text
)
RETURNS text
LANGUAGE sql
IMMUTABLE
AS $$
  SELECT encode(
    digest(COALESCE(normalize_whitespace(post_text), ''), 'sha256'),
    'hex'
  );
$$;

CREATE OR REPLACE FUNCTION build_linkedin_post_dedup_key(
  post_url text,
  author_profile text,
  published_at timestamptz,
  post_text text
)
RETURNS text
LANGUAGE sql
IMMUTABLE
AS $$
  SELECT COALESCE(
    CASE
      WHEN extract_linkedin_post_stable_id(post_url) IS NOT NULL
        THEN 'li:' || extract_linkedin_post_stable_id(post_url)
      ELSE NULL
    END,
    CASE
      WHEN canonicalize_linkedin_post_url(post_url) IS NOT NULL
        THEN 'url:' || canonicalize_linkedin_post_url(post_url)
      ELSE NULL
    END,
    'fp:' || encode(
      digest(
        concat_ws(
          '|',
          COALESCE(canonicalize_linkedin_post_url(author_profile), ''),
          COALESCE(to_char(published_at AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"'), ''),
          COALESCE(normalize_whitespace(post_text), '')
        ),
        'sha256'
      ),
      'hex'
    )
  );
$$;

CREATE OR REPLACE FUNCTION sync_linkedin_post_dedup_fields()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
  NEW.canonical_url := canonicalize_linkedin_post_url(NEW.url);
  NEW.normalized_text := COALESCE(normalize_whitespace(NEW.text), '');
  NEW.content_hash := build_linkedin_post_content_hash(NEW.text);
  NEW.canonical_post_key := build_linkedin_post_dedup_key(
    NEW.url,
    COALESCE(NEW.raw_payload ->> 'author_profile', ''),
    NEW.posted_at,
    NEW.text
  );

  IF NEW.first_seen_at IS NULL THEN
    NEW.first_seen_at := COALESCE(NEW.created_at, NEW.observed_at, now());
  END IF;

  IF NEW.last_seen_at IS NULL THEN
    NEW.last_seen_at := COALESCE(NEW.observed_at, NEW.updated_at, now());
  END IF;

  RETURN NEW;
END;
$$;

ALTER TABLE linkedin_posts
  ADD COLUMN IF NOT EXISTS canonical_url text,
  ADD COLUMN IF NOT EXISTS normalized_text text,
  ADD COLUMN IF NOT EXISTS content_hash text,
  ADD COLUMN IF NOT EXISTS canonical_post_key text,
  ADD COLUMN IF NOT EXISTS first_seen_at timestamptz,
  ADD COLUMN IF NOT EXISTS last_seen_at timestamptz,
  ADD COLUMN IF NOT EXISTS last_comment_generated_at timestamptz;

UPDATE linkedin_posts
SET
  canonical_url = canonicalize_linkedin_post_url(url),
  normalized_text = COALESCE(normalize_whitespace(text), ''),
  content_hash = build_linkedin_post_content_hash(text),
  canonical_post_key = build_linkedin_post_dedup_key(
    url,
    COALESCE(raw_payload ->> 'author_profile', ''),
    posted_at,
    text
  ),
  first_seen_at = COALESCE(first_seen_at, created_at, observed_at, now()),
  last_seen_at = COALESCE(
    last_seen_at,
    observed_at,
    updated_at,
    created_at,
    now()
  );

WITH ranked AS (
  SELECT
    id,
    canonical_post_key,
    first_value(id) OVER (
      PARTITION BY canonical_post_key
      ORDER BY
        COALESCE(posted_at, observed_at, created_at) ASC,
        created_at ASC,
        id ASC
    ) AS survivor_id,
    row_number() OVER (
      PARTITION BY canonical_post_key
      ORDER BY
        COALESCE(posted_at, observed_at, created_at) ASC,
        created_at ASC,
        id ASC
    ) AS rn
  FROM linkedin_posts
  WHERE canonical_post_key IS NOT NULL
),
stats AS (
  SELECT
    survivor_id,
    min(first_seen_at) AS first_seen_at_min,
    max(last_seen_at) AS last_seen_at_max,
    max(observed_at) AS observed_at_max
  FROM ranked r
  JOIN linkedin_posts p ON p.id = r.id
  GROUP BY survivor_id
)
UPDATE linkedin_posts p
SET
  first_seen_at = s.first_seen_at_min,
  last_seen_at = s.last_seen_at_max,
  observed_at = GREATEST(p.observed_at, s.observed_at_max)
FROM stats s
WHERE p.id = s.survivor_id;

WITH ranked AS (
  SELECT
    id,
    row_number() OVER (
      PARTITION BY canonical_post_key
      ORDER BY
        COALESCE(posted_at, observed_at, created_at) ASC,
        created_at ASC,
        id ASC
    ) AS rn
  FROM linkedin_posts
  WHERE canonical_post_key IS NOT NULL
)
DELETE FROM linkedin_posts p
USING ranked r
WHERE p.id = r.id
  AND r.rn > 1;

ALTER TABLE linkedin_posts
  ALTER COLUMN canonical_url SET NOT NULL,
  ALTER COLUMN normalized_text SET NOT NULL,
  ALTER COLUMN content_hash SET NOT NULL,
  ALTER COLUMN canonical_post_key SET NOT NULL,
  ALTER COLUMN first_seen_at SET NOT NULL,
  ALTER COLUMN last_seen_at SET NOT NULL,
  ALTER COLUMN first_seen_at SET DEFAULT now(),
  ALTER COLUMN last_seen_at SET DEFAULT now();

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'linkedin_posts_normalized_text_chk'
  ) THEN
    ALTER TABLE linkedin_posts
      ADD CONSTRAINT linkedin_posts_normalized_text_chk
      CHECK (btrim(normalized_text) <> '');
  END IF;

  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'linkedin_posts_content_hash_chk'
  ) THEN
    ALTER TABLE linkedin_posts
      ADD CONSTRAINT linkedin_posts_content_hash_chk
      CHECK (content_hash ~ '^[0-9a-f]{64}$');
  END IF;

  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'linkedin_posts_canonical_post_key_chk'
  ) THEN
    ALTER TABLE linkedin_posts
      ADD CONSTRAINT linkedin_posts_canonical_post_key_chk
      CHECK (btrim(canonical_post_key) <> '');
  END IF;
END;
$$;

CREATE UNIQUE INDEX IF NOT EXISTS linkedin_posts_canonical_post_key_uidx
  ON linkedin_posts(canonical_post_key);

CREATE INDEX IF NOT EXISTS linkedin_posts_content_hash_idx
  ON linkedin_posts(content_hash);

CREATE INDEX IF NOT EXISTS linkedin_posts_last_seen_idx
  ON linkedin_posts(last_seen_at DESC);

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_trigger
    WHERE tgname = 'linkedin_posts_sync_dedup_fields'
  ) THEN
    CREATE TRIGGER linkedin_posts_sync_dedup_fields
    BEFORE INSERT OR UPDATE OF url, text, posted_at, raw_payload
    ON linkedin_posts
    FOR EACH ROW
    EXECUTE FUNCTION sync_linkedin_post_dedup_fields();
  END IF;
END;
$$;

COMMIT;
