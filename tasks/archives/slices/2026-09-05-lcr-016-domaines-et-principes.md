# LCR-016 — Les domaines portent les principes

**Spec** : `tasks/specs/2026-09-05-domaines-et-principes-spec.md`
**Statut** : done, mesuré

## Fichiers touchés

- `app/linkedin_comments/profil.py` — les six domaines portent les douze principes.
- `app/linkedin_comments/prompts.py` — `lcr-v4-domaines`. Analyseur par domaine, sélecteur supprimé, règles d'écriture et cinq exemples au rédacteur, juge à trois questions.
- `app/linkedin_comments/controls.py` — 250 lignes à 130, quatre règles objectives.
- `app/linkedin_comments/runtime.py` — chaîne domaines vers principes, trois appels de modèle au lieu de quatre.
- `app/linkedin_comments/contracts.py` — `domaines` remplace `tags_situation`, `SelectionResult` et `evidence_ids` supprimés.
- `app/linkedin_comments/corpus.py`, `corpus.json`, `tests/linkedin_comments/test_corpus.py` — supprimés.
- `app/config.py`, `.env.example`, `dry_run.py`, use case — `COMMENT_SELECTOR_MAX_TOKENS` retiré.
- `README.md`, `docs/ARCHITECTURE.md`, `CLAUDE.md`, `AGENTS.md` — alignés.

## Vérification

    ./.venv/bin/pytest tests -q          # 101 passed

    OLLAMA_MODEL=qwen3.5:9b OLLAMA_THINK=false \
      ./.venv/bin/python -u -m app.linkedin_comments.dry_run --world icp1 \
      --fixtures tasks/evidence/lcr-015/feed-consultant-2026-09-05.json \
      --output tasks/evidence/lcr-016/quatrieme-essai.json --verbose

Résultat : 8 brouillons, 8 skips, 0 erreur sur 17 posts.

## Reste à faire

1. Rejouer le lot de véracité contre le juge réécrit.
2. Reconstruire l'image, sinon l'API sert l'ancien moteur.
3. Traiter l'anglicisme « supporter » passé dans un brouillon.
