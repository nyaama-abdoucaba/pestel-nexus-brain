-- Catégorie 'ai_practitioner'.
-- Vocabulaire du domaine, aucune donnée personnelle.
-- Les praticiens nommés vivent hors du dépôt, voir db/seeds/README.md.

BEGIN;

INSERT INTO target_categories (slug, label, description)
VALUES (
  'ai_practitioner',
  'Praticien IA',
  $description$Personne suivie pour sa pratique concrète de l'intelligence artificielle.$description$
)
ON CONFLICT (slug) DO UPDATE
SET
  label = EXCLUDED.label,
  description = EXCLUDED.description;

COMMIT;
