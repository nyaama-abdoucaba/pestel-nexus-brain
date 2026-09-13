# Vue d'ensemble du dépôt

Le dépôt contient un seul produit actif : le runtime de commentaires LinkedIn sous `app/`.

**Pour comprendre comment il fonctionne, lire `docs/ARCHITECTURE.md`.** Ce fichier-ci ne donne que la carte des dossiers.

- `app/linkedin_comments/` : logique IA explicite et contrôles.
- `app/infrastructure/postgres/` : accès à PostgreSQL.
- `db/init/` : schéma local.
- `ui/` : vues de lecture PostgreSQL pour les posts et les cibles LinkedIn.
- `tasks/` : décisions et découpage du travail.

Les outils de collecte et de digest n8n restent hors de ce dépôt. Il n'existe aucun proxy ni runtime cloud dans cette architecture.
