# Conteneurisation de brain-api

## Contexte

`brain-api` (FastAPI, port 8000) tourne en natif. `infra/services.yaml` documente
sa commande de démarrage mais `scripts/stack.sh start` ne la lance jamais : le
service reste éteint tant que personne n'y pense. C'est la cause du dernier
incident : le pont n8n (LCR-009) appelait un port mort.

## Objectif

Faire tourner `brain-api` dans le même cycle de vie que `pestel-postgres` :
démarré par `docker compose`, visible dans `stack.sh status`, plus d'oubli
manuel possible.

- Image buildée depuis le `Dockerfile` existant à la racine.
- Service ajouté à `docker-compose.db.yml`, réseau `pestel_shared` (déjà
  utilisé par `pestel-postgres` et par `n8n-app`).
- `DATABASE_URL` pointe vers `pestel-postgres:5432` (nom de service, plus
  `localhost`).
- `OLLAMA_URL` pointe vers `host.docker.internal:11434` : Ollama reste natif
  pour l'accès GPU Metal, seul le conteneur change de cible.
- `infra/services.yaml` mis à jour : `runtime: docker`, healthcheck inchangé
  (`http://localhost:8000/health`, le port reste publié sur l'hôte).

## Hors périmètre

- Changer l'URL appelée par le nœud n8n : `host.docker.internal:8000` reste
  valide, le port est toujours publié sur l'hôte.
- Toucher à la logique applicative (`app/`).
- Conteneuriser Ollama.
