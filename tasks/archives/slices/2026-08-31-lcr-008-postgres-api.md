# LCR-008 — Persistance PostgreSQL et API

**Spec** : `2026-08-31-linkedin-comment-runtime-spec.md`  
**Statut** : ✅ done  
**Effort** : M

## Livré

- Table `linkedin_comment_runs` et index de lecture par post/statut.
- Repository PostgreSQL dédié, sans dépendance à une persistance héritée.
- Endpoint `POST /v1/linkedin-comment-runs`.
- Erreurs distinctes : post absent (404), Ollama ou PostgreSQL indisponible (503).

## Vérification

Tests API mockés dans `tests/linkedin_comments/test_api.py`.
