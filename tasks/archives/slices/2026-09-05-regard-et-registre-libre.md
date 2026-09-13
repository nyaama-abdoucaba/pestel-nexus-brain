# LCR-014 — Le regard, et le registre libre

**Spec** : `tasks/specs/2026-09-05-regard-et-registre-libre-spec.md`
**Statut** : done, mesure du juge à faire

## Fichiers touchés

- `app/linkedin_comments/profil.py` — nouveau, six domaines et leur filtrage par monde.
- `app/linkedin_comments/prompts.py` — rédacteur unique, structures imposées retirées, mouvements libres, garde-fou anti-fabrication ajouté au juge.
- `app/linkedin_comments/worlds.py` — `ancrage_requis` retiré.
- `app/linkedin_comments/runtime.py` — plus de skip sans ancrage, rédacteur unifié, mode `libre`.
- `app/linkedin_comments/controls.py` — `check_ends_on_question` et `check_declarative_budget` supprimés, bornes unifiées à 1-4 phrases et 30 mots.
- `README.md`, `docs/ARCHITECTURE.md` — mis à jour.

## Vérification

    ./.venv/bin/pytest tests -q          # 147 passed

## Reste à faire

1. Reconstruire l'image, sinon l'API sert l'ancien moteur.
2. Rejouer le lot des 12 consultants et lire les brouillons.
3. Monter le jeu de test du juge : une dizaine de brouillons dont la moitié contient un vécu fabriqué, mesurer combien il en attrape.
