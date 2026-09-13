---
name: n8n-pestelnexus
description: Notes opérationnelles pour les workflows n8n du runtime de commentaires LinkedIn.
---

# n8n — Pestel Nexus

## Rôle de n8n

n8n collecte les posts LinkedIn, déclenche le runtime Python et prépare le digest. Il ne porte pas de prompt, de validation éditoriale ni de décision de publication.

## Appel du runtime

Le nœud HTTP appelle l'API locale :

```text
POST http://host.docker.internal:8000/v1/linkedin-comment-runs
```

Le corps contient l'identifiant PostgreSQL du post à traiter et `reader_world`
(par défaut `icp1`). Le runtime persiste seul le run, les diagnostics et le
résultat. Ne pas envoyer de `budget` tant que le contrat n8n ne l'expose pas.

## Règles

- Conserver les credentials de collecte séparés du runtime éditorial.
- Tester manuellement avant d'activer un déclencheur planifié.
- Le digest ne lit que les runs finalisés dans PostgreSQL.
