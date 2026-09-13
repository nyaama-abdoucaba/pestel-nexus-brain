# LCR-015 — Conversation ICP1, audit et compatibilité

Statut : en cours.
Spec : ../specs/2026-09-05-commentaires-conversation-audit.md

Plan : aligner politique/rédacteur/juge/contrôles ; journaliser les appels ; ajouter une évaluation reproductible ; calibrer sur le feed réel ; vérifier API/PostgreSQL/n8n et les autres mondes ; documenter et commit.

Constat initial : LCR-014 déjà présent sur main, sans modification locale. Les contrôles imposent encore félicitations interdites/sujet concret/nom propre ; prompt_version reste lcr-v2 malgré la refonte. La déduplication du workflow repose sur post+hash, tous mondes et versions confondus : une relance du feed déjà traité ne mesure donc pas une nouvelle politique.

État de reprise : [reste à faire complet](../RESTE-A-FAIRE-COMMENTAIRES-ICP1.md). Premier essai terminé : 1 draft, 15 skips, 1 erreur ; prompts du juge corrigés depuis, non encore évalués. 81 tests ciblés réussis.
