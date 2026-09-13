# Local Dev

## Environnement
- Python virtualenv attendu à la racine du repo: `./.venv`
- Variables d’environnement du runtime principal dans `.env`
- Variables d’environnement du runtime dans `.env` : `DATABASE_URL`, `OLLAMA_URL` et le modèle.

## Vérification rapide
1. Activer l’environnement si nécessaire.
2. Exécuter `./scripts/verify.sh`
3. Corriger toute régression avant de continuer

## Base existante

`db/init/` ne s'applique automatiquement que sur un volume PostgreSQL neuf.
Pour une base locale déjà créée, appliquer uniquement les scripts nécessaires
de `db/migrations/` après revue du contenu.
