# AGENTS.md

## Objectif du repo
- Faire évoluer `pestel-nexus-brain` par petits changements relisibles, testés et compatibles avec les contrats externes.

## Mode opératoire — être paresseux
- Si l'utilisateur peut exécuter une commande en 10 secondes, lui demander de le faire plutôt que de scripter.
- Ne pas générer de code ou de texte qui n'est pas demandé.
- Réponses courtes par défaut. Développer seulement si la complexité le justifie.
- Lire le minimum de fichiers nécessaires avant d'agir.
- Poser une question ciblée plutôt que d'explorer en aveugle.

## Commandes canoniques
- Tests: `./.venv/bin/pytest tests -q`
- Vérification locale: `./scripts/verify.sh` (alias de `./.venv/bin/pytest tests -q`)

## Workflow non négociable
- `Explore -> Plan -> Implement -> Verify -> Review`
- Pas de changement non trivial sans `tasks/specs/*` et `tasks/slices/*`
- Pas de merge sans preuve de vérification

## Règle hotfix

Un hotfix (production cassée, endpoint en 400, données perdues) ne suspend pas le process.

- Coder le fix est autorisé en priorité
- La spec et la slice **doivent être créées dans la même session**, avant de passer à autre chose
- La slice est marquée `done` mais doit documenter que c'est un hotfix rétroactif
- "C'était urgent" n'est pas une raison suffisante pour omettre la traçabilité

## Architecture
- Les routes HTTP restent minces.
- Les use cases dispatchent les flux métier.
- Les workflows métier portent l’orchestration.
- Les adapters techniques vivent dans `app/infrastructure`.

## Sécurité
- Jamais de secret en dur.
- Toute évolution DB ou workflow à effet de bord passe par une spec dédiée.
