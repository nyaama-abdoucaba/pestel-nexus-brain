# CCAR-000 : atelier archivé, vitrine publique neuve

**Statut** : done, vérifié le 2026-09-13
**Epic** : EPIC-CCAR, lot L0
**Spec** : `tasks/specs/2026-09-13-ccar-000-atelier-vitrine-spec.md`
**Branche** : aucune, lot d'amorçage (voir la spec)

## Règle d'entrée

- [x] Une spec la couvre.
- [x] Ses critères d'acceptation sont écrits et testables.
- [x] Aucune inconnue technique ne bloque son chemin.
- [x] Les fichiers et dépôts touchés sont identifiés.
- [x] L'epic EPIC-CCAR est validé par Abdoulaye, le 2026-09-13.

## Le symptôme

Abdoulaye veut un dépôt public. Le dépôt privé suivait des fichiers qui nommaient
des personnes réelles, avec des appréciations privées. Les sortir du suivi ne
suffit pas : l'historique Git les conserve, et un dépôt public expose l'historique.

## Ce qui a été changé

**Avant l'exécution**, dans les fichiers :

- Données nominatives sorties vers `../donnees-privees/` : sourcing, imports,
  cibles des seeds `001` et `002`, preuves de LCR-015, LCR-016 et LCR-019.
- Seeds coupés en deux : les catégories restent, les personnes sortent.
- Un nom d'auteur anonymisé dans `tasks/RESTE-A-FAIRE-COMMENTAIRES-ICP1.md`.
- Règles `.gitignore` ajoutées, règle des preuves écrite dans `tasks/evidence/README.md`.

**Pendant l'exécution**, par Abdoulaye, les sept étapes de la spec :

| Étape | Geste | Résultat |
|---|---|---|
| 1 | commit final poussé vers l'atelier | `a56e7f3` présent sur GitHub |
| 2 | `.git` mis de côté | `../pestel-nexus-brain-atelier.git` |
| 3 | histoire neuve | un commit, 141 fichiers |
| 4 | `gh repo rename` | `pestel-nexus-brain-atelier` |
| 5 | sauvegarde rebranchée | `origin` pointe vers `-atelier.git` |
| 6 | `gh repo create --public` | 188 objets poussés |
| 7 | `gh repo archive` | atelier en lecture seule |

## La mesure

| Critère | Commande | Attendu | Obtenu |
|---|---|---|---|
| C1 vitrine publique | `gh repo view ... --json visibility` | `PUBLIC` | `PUBLIC` |
| C2 un seul commit | `git log --oneline` en local et via `gh api` | 1 et 1 | 1 et 1 |
| C3 atelier archivé | `gh repo view ...-atelier --json isArchived` | `true` | `true` |
| C4 sauvegarde rebranchée | `git --git-dir=... remote get-url origin` | `...-atelier.git` | `...-atelier.git` |
| C5 tests | `./scripts/verify.sh` | tous verts | 109 réussis |
| C6 aucune donnée nominative publiée | `git grep` sur `HEAD` | 2 fichiers attendus, 0 donnée | conforme |
| C7 l'atelier porte le commit final | comparaison locale et GitHub | même SHA | `a56e7f3` des deux côtés |

Le critère C7 ne figurait pas dans la spec. Il a été ajouté à la vérification :
l'étape 1 n'avait pas été collée, et un atelier archivé refuse tout push. Si le
commit final avait manqué, il aurait fallu désarchiver pour le pousser.

## La prise nette

Le même dossier local, le même chemin, les mêmes volumes Docker. Deux mémoires
Git différentes derrière :

    pestel-nexus-brain/            git log : 1 commit      public
    pestel-nexus-brain-atelier.git git log : tout l'historique depuis avril, archivé

## Le coût

**L'historique de la vitrine commence le 2026-09-13.** Un `git blame` ou un
`git log` sur la vitrine ne dit rien des décisions antérieures. Pour comprendre
pourquoi une ligne de code existe, il faut désormais aller lire l'atelier.

**Les données privées n'ont plus de copie hors de ce Mac.** Les fichiers de
`../donnees-privees/` ne sont suivis par aucun dépôt. Aucune destination Time
Machine n'est configurée. Les anciennes versions survivent dans l'historique de
l'atelier, mais les deux fichiers de cibles issus du découpage des seeds
n'existent qu'en un exemplaire.

## Les limites

La spec annonçait « autour de 142 fichiers ». Le décompte de 142 incluait les
quatre fichiers `ops/` encore suivis dans l'ancien index. La vitrine en a exclu
ces quatre et ajouté l'epic, la spec et la slice : 142 moins 4 plus 3 donne 141.

Le comportement de la redirection GitHub après renommage n'a pas été observé.
L'étape 5 le rendait sans objet.

Le contrôle C6 repose sur deux motifs de recherche. Il détecte une URL de profil
ou un champ d'auteur. Il ne détecte pas un nom de personne écrit en clair dans un
texte libre : le balayage de ce cas a été fait à la main, avant l'exécution.

## Le reste à faire

1. **Corriger la règle Git de `CLAUDE.md`**, qui impose encore « Pas de branches.
   Pas de PR. ». Tout agent qui lit ce fichier commitera sur `main`, y compris
   l'action GitHub du lot L2b. Première tâche du lot L1.
2. **Sauvegarder `../donnees-privees/`.** Point métier : choisir où vivent des
   données nominatives en dehors de ce Mac.
3. **Choisir une licence pour la vitrine.** Point métier : sans licence, le code
   est consultable mais aucune réutilisation n'est autorisée.
4. **Protéger la branche `main` de la vitrine.** À décider dans CCAR-001.
