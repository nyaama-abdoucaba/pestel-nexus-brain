# Backlog

## Certification CCAR-F

Epic : `tasks/epics/2026-09-13-epic-ccar.md`. Découpage juste à temps : seul le lot
en cours porte une spec.

| Slice | Statut | Suite |
|---|---|---|
| CCAR-000 | ✅ done | Atelier archivé, vitrine publique neuve, aucune donnée nominative publiée |
| CCAR-001 | todo | `CLAUDE.md` sans contradiction. Sous-epic `tasks/epics/2026-09-15-epic-ccar-cc.md` |
| CCAR-002 à CCAR-007 | todo | Permissions, règles `paths`, skills, revue voies A et B. Voir le sous-epic |
| L3 à L7 | en attente | Voir l'epic parent |

## Runtime de commentaires LinkedIn

| Slice | Statut | Suite |
|---|---|---|
| LCR-001 à LCR-006 | ✅ done | Contrats, client Ollama, analyse, rédaction, guard et judge |
| LCR-008 | ✅ done | PostgreSQL et endpoint HTTP |
| LCR-009 | prêt pour test manuel | Tester le pont n8n vers l'API locale et le digest v2 |
| LCR-011 | ✅ done | Déduplication par hash dans l'historique du runtime |
| VIS-B-001 | prêt à appliquer | Appliquer la migration URL puis valider les candidates famille B |
| LCR-007 | todo | Calibrer ensemble prompts et paramètres sur le corpus |
| LCR-010 | ✅ done | Retrait complet du runtime et des surfaces héritées |
| CLEAN-2026-09-01 | ✅ done | Arborescence, schéma et documentation alignés sur le runtime actif |
| BRAIN-API-DOCKER | ✅ done | `brain-api` conteneurisé dans `docker-compose.db.yml`, plus d'oubli de démarrage manuel |
| LCR-016 | ✅ done, mesuré | Les domaines portent les principes, corpus supprimé. 8 brouillons sur 17 contre 1 avant |
| LCR-014 | ✅ done, mesure à faire | Le regard remplace l'ancrage obligatoire. Mesurer la fiabilité du juge sur le vécu fabriqué avant de s'y fier |
| LCR-012 | ✅ done, sorties à relire | Registre des mondes, monde `ai_practitioner` sans ancrage obligatoire, mode question. Corrige au passage le découpage décimal, l'extraction des nombres, les consignes de réécriture et `OLLAMA_THINK` sur un modèle à raisonnement |
| LCR-013 | sans suite | Écarter les posts personnels : refusé le 03/09/2026. Rien n'est publié automatiquement, chaque brouillon est relu à la main |

## Chantier en cours — LCR-015

Conversation ICP1, audit des appels et compatibilité multi-cibles : **en cours, non déployé**. Tests ciblés : 81 réussis. Premier essai réel : 1 draft / 15 skips / 1 erreur ; derniers prompts encore à évaluer.

Voir [le reste à faire complet](RESTE-A-FAIRE-COMMENTAIRES-ICP1.md).
