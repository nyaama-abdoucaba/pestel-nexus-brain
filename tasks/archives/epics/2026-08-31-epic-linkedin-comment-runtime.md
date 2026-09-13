# Epic — Runtime explicite de commentaires LinkedIn

**Statut** : en cours  
**Code** : EPIC-LCR  
**Nature** : transformation technique du runtime éditorial

## Objectif

Construire un runtime Python explicite, traçable et révisable pour les
commentaires LinkedIn :

```text
Analyse + ancrage → rédaction → guard déterministe → judge LLM
                                                    │
                         réécriture ◄───────────────┘
```

Le runtime utilise Ollama via le SDK Python `anthropic` (`gemma4:31b-cloud`). Il
ne dépend d'aucun runtime hérité. n8n ne conserve que la collecte, le
déclenchement et le digest.

## Contrat d’architecture

1. L’analyseur LLM décide `commentable` ou `skip` et produit les IDs de preuve.
2. Le rédacteur LLM ne reçoit que le post, la langue imposée, le contrat
   d’ancrage et les défauts précis précédents.
3. Le guard Python bloque les erreurs mécaniques avant le judge.
4. Le judge LLM retourne `approve`, `rewrite` ou `reject`.
5. Le budget de durée, tokens et révisions détermine la sortie
   `needs_human_review`; aucune approbation par défaut.

## Slices

| Code | Slice | Statut |
|---|---|---|
| LCR-001 | Contrats et corpus | ✅ done |
| LCR-002 | Client Anthropic/Ollama | ✅ done |
| LCR-003 | Analyseur | ✅ done |
| LCR-004 | Rédacteur | ✅ done |
| LCR-005 | Guard | ✅ done |
| LCR-006 | Judge + boucle | ✅ done |
| LCR-007 | Calibration | todo — corpus annoté à conduire ensemble |
| LCR-008 | PostgreSQL + API | ✅ done |
| LCR-009 | Bascule n8n | en attente de test d’intégration contrôlé |
| LCR-010 | Retrait legacy | ✅ done — noyau éditorial hérité retiré |

## Hors périmètre

- Plan commercial LinkedIn et publication automatique.
- Autres flux éditoriaux, changement de fournisseur LLM, UI générale.
- Suppression de l’ancien chemin avant que le nouveau soit testé sur le corpus.

## Critères de bascule

La bascule devient possible après application de la migration PostgreSQL,
installation de la dépendance `anthropic`, test d’un échantillon annoté et
branchement du collecteur n8n sur l’endpoint du runtime.
