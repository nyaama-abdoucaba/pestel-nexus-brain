# LCR-011 — Déduplication par contenu traité

**Spec** : `2026-09-03-linkedin-runtime-dedup-spec.md`
**Statut** : done

- Ajoute `content_hash` à l'historique des runs.
- Aligne la sélection n8n sur les runs `draft` et `skip` du runtime.
- Retire la dépendance au registre legacy `linkedin_post_processing_runs`.
