# Conteneurisation de brain-api

**Spec** : `2026-09-03-brain-api-containerization-spec.md`
**Statut** : ✅ done
**Effort** : S

## Livré

`brain-api` tourne désormais dans `docker-compose.db.yml` (service `brain-api`,
conteneur `pestel-brain-api`), build depuis le `Dockerfile` existant, réseau
`pestel_shared`. `DATABASE_URL` pointe vers `pestel-postgres:5432`, `OLLAMA_URL`
vers `host.docker.internal:11434`. Port 8000 toujours publié sur l'hôte, donc
l'appel n8n existant (`host.docker.internal:8000`) reste valide sans changement.

`scripts/stack.sh start` le démarre désormais sans modification : il lance déjà
`docker compose -f docker-compose.db.yml up -d`. `infra/services.yaml` mis à
jour (`runtime: docker`).

## Vérifié

- `docker compose -f docker-compose.db.yml up -d --build brain-api` : conteneur
  sain (`healthy`).
- `./scripts/stack.sh status` : `brain-api` 🟢.
- `POST /v1/linkedin-comment-runs` avec un post réel : lecture PostgreSQL,
  appel Ollama, décision `skip` (`anti_corpus:actualite_ia`) renvoyée et
  journalisée. Chaîne complète confirmée, pas seulement `/health`.

## Suite — changement de modèle (même jour)

Le digest réel a montré 11 `ollama_indisponible` sur 24 posts : logs Ollama
(`~/.ollama/logs/server.log`) confirment des `429 Too Many Requests` sur
`/api/chat`, `gemma4:31b-cloud` passe par le relais `ollama.com`, rate-limité
sous charge n8n.

Changement : `OLLAMA_MODEL=qwen3.5:9b` (local, pas de relais cloud) dans
`docker-compose.db.yml`. `./.venv/bin/python -m app.linkedin_comments.check_ollama_format`
montre que ce modèle casse le contrat JSON avec `think` par défaut mais pas
avec `think=false` (inverse de Gemma) : `OLLAMA_THINK=false` ajouté en
conséquence. Revérifié par un appel réel : sortie JSON valide, décision
cohérente avec le run précédent sous `gemma4:31b-cloud`.

Reste à vérifier : un post qui aboutit à un vrai brouillon (`outcome: draft`),
pas seulement un `skip`, pour valider les étapes rédaction/jugement avec ce
modèle.
