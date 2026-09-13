# Copilot Instructions

- Respecte `AGENTS.md` comme source de vérité opératoire.
- Pour tout changement multi-fichiers: lire la spec et la slice avant de modifier le code.
- Préserver les contrats externes de `crew_service`: `POST /runs`, review/publish, ingestion, Supabase, n8n.
- Garder les routes API minces, déplacer la logique vers `application/`, `workflows/` et `infrastructure/`.
- Ne pas réintroduire de monolithe type `main.py`, `memory.py` ou `editorial_flow.py`.
- Exiger une preuve de vérification avant de considérer le travail comme terminé.
- Commandes canoniques de vérification : `./scripts/verify.sh` ou `./.venv/bin/pytest tests -q`.
