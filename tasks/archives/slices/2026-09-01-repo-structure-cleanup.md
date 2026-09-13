# Slice — nettoyage architecture du dépôt

## Statut

done

## Changements attendus

- Déplacer les tests runtime embarqués dans `app/linkedin_comments/tests` vers
  `tests/linkedin_comments`.
- Supprimer les caches, fichiers système locaux et restes `bot` / `proxy`.
- Retirer le `guard.py` obsolète au profit de `controls.py`.
- Aligner README, architecture, Dockerfile et inventaire infra sur le port API
  `8000` et le transport Ollama natif.
- Aligner `linkedin_comment_runs` sur `draft`, `skip`, `error` avec une
  migration pour les bases existantes.

## Vérification

- `./.venv/bin/pytest tests/linkedin_comments -q`
- `./scripts/verify.sh`
