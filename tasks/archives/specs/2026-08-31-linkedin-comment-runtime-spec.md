# Spec — Runtime explicite de commentaires LinkedIn

**Date** : 2026-08-31  
**Statut** : implémenté, bascule à valider  
**Code** : LCR  
**Epic** : EPIC-LCR

## Chemin actif cible

`POST /v1/linkedin-comment-runs` reçoit un `linkedin_post_id` et un
`reader_world` obligatoire. Le use case charge le post depuis PostgreSQL,
exécute le runtime et persiste un unique run.

```text
PostgreSQL → analyseur → rédacteur → guard → judge → PostgreSQL
                                      ↑             │
                                      └── rewrite ──┘
```

Le runtime retourne `outcome` avec `draft`, `skip` ou `error`. La colonne
historique `status` de `linkedin_comment_runs` stocke les mêmes valeurs.
Les brouillons, violations du guard et décisions du judge sont conservés dans
`revisions_payload`; l’analyse et les diagnostics sont conservés avec le run.

## Paramètres initiaux

| Rôle | Température | Budget de réponse |
|---|---:|---:|
| Analyseur | 0,1 | 1 200 |
| Rédacteur | 0,5 | 700 |
| Judge | 0,0 | 800 |

`RevisionBudget` configure le maximum de révisions, tokens et durée sans modifier
le code. Les valeurs de départ sont 4 réécritures, 6 000 tokens et 120 secondes.

## Persistence et migration

La migration `db/init/050_linkedin_comment_runs.sql` s’applique automatiquement
sur une base vide. Pour une base existante, elle doit être exécutée une fois via
`psql` ou pgAdmin; les scripts `db/init` ne sont pas rejoués par Docker sur un
volume existant.

## n8n

Le workflow principal `LinkedIn Apify to Ollama Comments`
(`Odr7h7W64hcOhbgS`) appelle directement le runtime avec `linkedin_post_id` et
`reader_world`. Il reste désactivé jusqu’au test manuel du digest. Les anciens
sous-workflows ne font plus partie du chemin actif.

## Tests requis

- post stoppé par l’analyseur avant rédaction;
- approbation après guard et judge;
- langue refusée par le guard puis réécriture guidée;
- réécriture du judge transmise au rédacteur;
- budget de boucle → revue humaine;
- healthcheck/extraction client mockés;
- route HTTP déléguée au use case.
