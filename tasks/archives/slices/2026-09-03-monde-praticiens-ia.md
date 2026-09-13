# Slice — monde `ai_practitioner` et mode question

Spec : `tasks/specs/2026-09-03-monde-praticiens-ia-spec.md`
Date : 2026-09-03. Statut : done, en attente de relecture des sorties.

## Fichiers touchés

- `app/linkedin_comments/worlds.py` — nouveau. Registre des quatre mondes déclarés.
- `app/linkedin_comments/runtime.py` — validation du monde, bifurcation vers le mode question, repli `post_type`, consignes rédigées en réécriture.
- `app/linkedin_comments/prompts.py` — anti-actualité pilotée par le monde, `question_prompt`, question du juge pilotée par le monde et par le mode.
- `app/linkedin_comments/controls.py` — découpage décimal, extraction des nombres, `check_ends_on_question`, `check_declarative_budget`, `explain_violation`, mode dans `ControlContext`.
- `app/linkedin_comments/contracts.py` — champ `comment_mode`.
- `app/linkedin_comments/corpus.json` — six ancrages ouverts à `ai_practitioner`. Aucun ancrage créé ni modifié.
- `app/linkedin_comments/dry_run.py` — tri par date de publication, affichage du mode, mondes déclarés dans l'aide.
- `docker-compose.db.yml`, `.env.example` — `OLLAMA_THINK=false`.
- `tests/linkedin_comments/test_runtime.py`, `test_controls.py` — quinze tests ajoutés ou repris.

## Vérification

    ./.venv/bin/pytest tests -q          # 142 passed

Dry-run sur les posts réels de la base :

    OLLAMA_MODEL=qwen3.5:9b OLLAMA_THINK=false \
      ./.venv/bin/python -m app.linkedin_comments.dry_run --world ai_practitioner --db --limit 12

## Ce qui n'a pas été testé

Le régime des mondes de vente n'a pas été rejoué sur des posts réels : la base ne
contient aucun post de la liste A. Seuls les tests unitaires couvrent la
non-régression de ce côté.
