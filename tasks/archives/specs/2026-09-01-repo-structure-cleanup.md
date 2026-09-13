# Nettoyage architecture du dépôt

## Contexte

La logique métier du LinkedIn Comment Runtime évolue vite. Après recentrage sur
le runtime Python, le dépôt contenait encore des restes d'anciens chemins :
tests au mauvais endroit, documents RAG obsolètes, références à l'ancien guard,
port API contradictoire et schéma SQL désaligné avec le contrat `RunOutcome`.

## Objectif

Rendre l'arborescence lisible et cohérente avec le produit actif :

- code applicatif dans `app/` ;
- tests dans `tests/` ;
- schéma SQL aligné avec `draft`, `skip`, `error` ;
- documentation d'entrée alignée avec `reader_world` et le port `8000` ;
- retrait des artefacts locaux ou hérités sans toucher à la logique métier.

## Hors périmètre

- Modifier la doctrine éditoriale.
- Recalibrer les prompts.
- Publier ou exécuter le workflow n8n de bout en bout.
