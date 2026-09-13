# LCR-010 — Retrait du runtime précédent

**Spec** : `2026-08-31-linkedin-comment-runtime-spec.md`  
**Statut** : ✅ done

Le dépôt ne conserve que le runtime local de commentaires LinkedIn : PostgreSQL,
Ollama et l'API HTTP minimale.

Ont été retirés : les routes et flux éditoriaux précédents, les clients de
persistance précédents, le bot, le proxy distant, les vues associées, leurs tests
et les procédures de déploiement devenues obsolètes.
