-- Catégories métier des cibles LinkedIn.
-- Vocabulaire du domaine, aucune donnée personnelle.
-- Les cibles nommées vivent hors du dépôt, voir db/seeds/README.md.

BEGIN;

INSERT INTO target_categories (slug, label, description)
VALUES
  ('bailleur_institution', 'Bailleur / institution', 'Pages d’institutions et bailleurs vues par l’écosystème conseil-développement.'),
  ('media_ecosysteme', 'Média écosystème', 'Médias et relais éditoriaux des conversations professionnelles.'),
  ('voix_ecosysteme', 'Voix écosystème', 'Communautés ou voix visibles de l’écosystème professionnel et tech.'),
  ('cabinet_conseil', 'Cabinet de conseil', 'Cabinet visible auprès des consultants ; cible de visibilité, pas de vente directe.'),
  ('consultant', 'Consultant', 'Consultant indépendant ou dirigeant de petit cabinet vivant de sa production écrite ; cible de vente.'),
  ('agence_esn_technique', 'Agence / ESN technique', 'Agence, intégrateur ou structure technique ; cible de vente.')
ON CONFLICT (slug) DO UPDATE
SET label = EXCLUDED.label,
    description = EXCLUDED.description;

COMMIT;
