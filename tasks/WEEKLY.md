# Suivi hebdomadaire

## Priorités

| Slice | Statut | Prochaine action |
|---|---|---|
| CCAR-000 | ✅ done | Vitrine publique en ligne, atelier archivé. Suite : L1, en commençant par la règle Git de `CLAUDE.md` |
| EPIC-CCAR-CC | validé | Ouvrir CCAR-001 : deux décisions à prendre sur `CLAUDE.md` et `CLAUDE.local.md` |
| BRAIN-API-DOCKER | ✅ done | `brain-api` conteneurisé, démarré par `stack.sh start` |
| LCR-009 | prêt pour test manuel | Lancer un échantillon depuis n8n (le port mort est corrigé), vérifier le digest v2 |
| LCR-011 | ✅ done | Déduplication n8n basée sur `linkedin_comment_runs.content_hash` |
| VIS-B-001 | prêt à appliquer | Appliquer la migration URL, vérifier les pages puis charger le seed |
| LCR-007 | todo | Construire et annoter le corpus de calibration |
| CLEAN-2026-09-01 | ✅ done | Nettoyage structurel vérifié du dépôt |
| LCR-016 | ✅ done, mesuré | Les domaines portent les principes, corpus supprimé. 8 brouillons sur 17 contre 1 avant |
| LCR-014 | ✅ done, mesure à faire | Le regard remplace l'ancrage obligatoire. Mesurer la fiabilité du juge sur le vécu fabriqué avant de s'y fier |
| LCR-012 | ✅ done, sorties à relire | Monde `ai_practitioner` et mode question. Relire les brouillons du dry-run avant d'ouvrir le mode question en production |

Le runtime actif se limite aux commentaires LinkedIn, PostgreSQL et Ollama.

## Chantier en cours — LCR-015

Conversation ICP1, audit des appels et compatibilité multi-cibles : **en cours, non déployé**. Tests ciblés : 81 réussis. Premier essai réel : 1 draft / 15 skips / 1 erreur ; derniers prompts encore à évaluer.

Voir [le reste à faire complet](RESTE-A-FAIRE-COMMENTAIRES-ICP1.md).
