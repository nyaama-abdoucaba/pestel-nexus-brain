BEGIN;

CREATE TABLE target_categories (
  slug text PRIMARY KEY,
  label text NOT NULL,
  description text,
  created_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT target_categories_slug_chk CHECK (
    slug ~ '^[a-z][a-z0-9_]*$'
  ),
  CONSTRAINT target_categories_label_chk CHECK (btrim(label) <> '')
);

CREATE TABLE linkedin_targets (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  linkedin_url text NOT NULL UNIQUE,
  why_follow text,
  status text NOT NULL DEFAULT 'candidate',
  scrape_enabled boolean NOT NULL DEFAULT false,
  last_scraped_at timestamptz,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT linkedin_targets_name_chk CHECK (btrim(name) <> ''),
  CONSTRAINT linkedin_targets_url_chk CHECK (
    linkedin_url ~ '^https://(www\.)?linkedin\.com/(in|company|school)/[^/?#]+/?$'
  ),
  CONSTRAINT linkedin_targets_status_chk CHECK (
    status IN ('candidate', 'active', 'paused', 'rejected')
  ),
  CONSTRAINT linkedin_targets_metadata_object_chk CHECK (
    jsonb_typeof(metadata) = 'object'
  )
);

CREATE TABLE linkedin_target_categories (
  linkedin_target_id uuid NOT NULL
    REFERENCES linkedin_targets(id) ON DELETE CASCADE,
  category_slug text NOT NULL
    REFERENCES target_categories(slug) ON DELETE CASCADE,
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (linkedin_target_id, category_slug)
);

CREATE INDEX linkedin_targets_status_idx
  ON linkedin_targets(status);

CREATE INDEX linkedin_targets_scrape_ready_idx
  ON linkedin_targets(last_scraped_at NULLS FIRST)
  WHERE status = 'active' AND scrape_enabled = true;

CREATE INDEX linkedin_target_categories_category_idx
  ON linkedin_target_categories(category_slug, linkedin_target_id);

CREATE TRIGGER linkedin_targets_touch_updated_at
BEFORE UPDATE ON linkedin_targets
FOR EACH ROW
EXECUTE FUNCTION touch_updated_at();

COMMIT;
