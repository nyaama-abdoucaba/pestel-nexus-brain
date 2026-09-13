# VIS-B-001 — Seed des candidats LinkedIn famille B

**Spec** : `2026-09-02-visibility-family-b-candidates.md`  
**Statut** : prêt à appliquer manuellement  

## Livré

Le seed `db/seeds/002_visibility_family_b_candidates.sql` contient 31 cibles
candidates : pages de visibilité et consultants. Il normalise leurs URLs,
crée les catégories, puis crée leurs associations. Il n'a pas été exécuté.

## Ordre d'application

1. Appliquer `2026-09-02-linkedin-target-url-kinds.sql`.
2. Vérifier manuellement les pages et le doublon DigitalAfrica.
3. Exécuter le seed.
