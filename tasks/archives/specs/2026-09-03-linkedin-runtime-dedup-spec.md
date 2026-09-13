# Spec — Déduplication du runtime LinkedIn

**Statut** : implémentée

`linkedin_comment_runs` est l'historique canonique des décisions du runtime.
Chaque run stocke l'empreinte du post traité. n8n sélectionne un post si aucun
run finalisé (`draft` ou `skip`) ne correspond au même post et au même hash.
Les erreurs restent relançables.

`linkedin_post_processing_runs` n'est pas réintroduite : ce registre legacy
était lu par le workflow, mais jamais alimenté.
