# CCAR-000 : atelier archivé, vitrine publique neuve

**Statut** : todo
**Epic** : EPIC-CCAR, lot L0
**Spec** : `tasks/specs/2026-09-13-ccar-000-atelier-vitrine-spec.md`
**Branche** : aucune, lot d'amorçage (voir la spec)

## Règle d'entrée

- [x] Une spec la couvre.
- [x] Ses critères d'acceptation sont écrits et testables.
- [x] Aucune inconnue technique ne bloque son chemin.
- [x] Les fichiers et dépôts touchés sont identifiés.
- [ ] L'epic EPIC-CCAR est validé par Abdoulaye.

## Le symptôme

Abdoulaye veut un dépôt public. Le dépôt privé suivait des fichiers qui nommaient
des personnes réelles, avec des appréciations privées. Les sortir du suivi ne
suffit pas : l'historique Git les conserve, et un dépôt public expose l'historique.

## Critères d'acceptation

- [ ] La vitrine `pestel-nexus-brain` est publique.
- [ ] Son historique compte un seul commit.
- [ ] L'atelier `pestel-nexus-brain-atelier` est archivé.
- [ ] La sauvegarde locale pointe vers l'atelier, pas vers la vitrine.
- [ ] `./scripts/verify.sh` passe.
- [ ] Aucun fichier nominatif dans la vitrine.

---

Les sections suivantes se remplissent après exécution.

## Ce qui a été changé

## La mesure

## Le coût

## Les limites

## Le reste à faire
