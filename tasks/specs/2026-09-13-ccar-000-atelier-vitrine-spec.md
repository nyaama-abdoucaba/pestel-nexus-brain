# Spec CCAR-000 : atelier archivé, vitrine publique neuve

**Epic** : EPIC-CCAR, lot L0
**Exigence PRD** : section 12.2, version 1.2
**Rédigée le** : 2026-09-13

## Ce que cette spec décrit

Le passage d'un dépôt GitHub unique et privé à deux dépôts : un atelier privé
archivé qui garde tout l'historique, et une vitrine publique dont l'histoire
commence au premier commit.

## La carte

```text
AVANT
  dossier local pestel-nexus-brain/
    .git/  ── origin ──►  github: pestel-nexus-brain  (privé, 30 commits en retard)

APRÈS
  dossier local pestel-nexus-brain/          (mêmes fichiers, même chemin)
    .git/  ── origin ──►  github: pestel-nexus-brain           (public, 1 commit)

  dossier local pestel-nexus-brain-atelier.git/   (ancienne mémoire, à côté)
           ── origin ──►  github: pestel-nexus-brain-atelier   (privé, archivé)

  dossier local donnees-privees/             (hors de tout suivi Git)
```

## Pourquoi le même dossier

Deux dépendances interdisent de déplacer le code.

`docker-compose.db.yml` ne fixe pas de nom de projet. Docker Compose le déduit du
nom du dossier. Un autre dossier créerait des volumes vides, et la base PostgreSQL
semblerait perdue.

`.venv/` grave des chemins absolus dans ses scripts. Déplacé, il casse.

La spec remplace donc seulement le dossier caché `.git/`, qui porte toute la
mémoire Git. Les fichiers ordinaires ne bougent pas.

## Préalables, faits le 2026-09-13

- Données personnelles sorties vers `../donnees-privees/`.
- Seeds `001` et `002` coupés, catégories gardées.
- Preuves de run sorties, règle écrite dans `tasks/evidence/README.md`.
- Un nom d'auteur anonymisé.
- Contrôle : aucun fichier embarqué ne contient `author_name` ni une URL de profil.

## Une exception au process, et sa raison

Ce lot ne passe ni par une branche ni par une PR. La vitrine n'existe pas encore :
il n'y a aucun dépôt sur lequel ouvrir une PR. C'est le problème classique de
l'amorçage.

La règle branche plus PR s'applique à partir de CCAR-001, premier lot joué sur la
vitrine.

## Les étapes

Chaque étape donne sa commande, ce qu'on doit voir, et comment revenir en arrière.
Les commandes se lancent depuis `pestel-nexus-brain/`.

### Étape 1 : pousser l'état final vers l'atelier

```bash
git add -A && git commit -m "chore: etat final de l'atelier avant archivage"
```

```bash
git push origin main
```

Attendu : une ligne `main -> main`.

Contrôle, qui doit afficher `0` :

```bash
git fetch origin && git rev-list --count origin/main..main
```

Retour arrière : aucun nécessaire. Un push vers un dépôt privé ne publie rien.

### Étape 2 : mettre la mémoire Git de côté

```bash
mv .git ../pestel-nexus-brain-atelier.git
```

Attendu : aucune sortie. `git status` répond désormais « not a git repository ».

Retour arrière : `mv ../pestel-nexus-brain-atelier.git .git`

### Étape 3 : créer l'histoire neuve

```bash
git init -b main && git add -A
```

Contrôle des profils, qui ne doit lister que le seed `.example` et
`ui/views/linkedin_targets.py`. Le premier contient des personnages inventés, le
second un texte d'aide `linkedin.com/in/...` :

```bash
git grep -l "linkedin.com/in/" -- . ':!tests' ':!tasks/specs'
```

Contrôle des fichiers de données, qui ne doit rien afficher. Il ne cherche que
dans les JSON, CSV, SQL et le markdown de `tasks/`, parce que `author_name` est un
nom de champ légitime du code, dans `contracts.py` par exemple :

```bash
git grep -lE "author_name|linkedin\.com/posts" -- '*.json' '*.csv' '*.sql' 'tasks/*.md' ':!app/linkedin_comments/fixtures' ':!tasks/specs' ':!tasks/evidence/README.md'
```

La fixture `archived_posts_sample.json` est exclue en connaissance de cause : ses
auteurs sont marqués « Fixture synthétique, non un post réel ».

Contrôle du volume, attendu autour de 142 :

```bash
git ls-files | wc -l
```

Si un contrôle échoue : `rm -rf .git` puis corriger, puis reprendre l'étape 3.
Ce `rm -rf` ne détruit que l'histoire neuve, encore vide. L'ancienne mémoire est
à l'abri depuis l'étape 2.

```bash
git commit -m "Premier commit public de pestel-nexus-brain"
```

Attendu : `git log --oneline` affiche une seule ligne.

### Étape 4 : libérer le nom sur GitHub

```bash
gh repo rename pestel-nexus-brain-atelier --repo nyaama-abdoucaba/pestel-nexus-brain
```

Attendu : un message de confirmation du renommage.

Retour arrière : `gh repo rename pestel-nexus-brain --repo nyaama-abdoucaba/pestel-nexus-brain-atelier`

### Étape 5 : rebrancher la sauvegarde sur le bon nom

```bash
git --git-dir=../pestel-nexus-brain-atelier.git remote set-url origin git@github.com:nyaama-abdoucaba/pestel-nexus-brain-atelier.git
```

Cette étape passe avant la création de la vitrine. Dès que la vitrine prendra
l'ancien nom, la redirection GitHub disparaîtra. Sans cette commande, la
sauvegarde pointerait vers le dépôt public, et un push accidentel y enverrait
l'ancien historique.

### Étape 6 : publier la vitrine

```bash
gh repo create nyaama-abdoucaba/pestel-nexus-brain --public --source=. --remote=origin --push
```

Attendu : l'URL du dépôt, puis une ligne `main -> main`.

Retour arrière : `gh repo delete nyaama-abdoucaba/pestel-nexus-brain`. Cette
commande supprime définitivement le dépôt public. Elle ne touche ni l'atelier ni
les fichiers locaux.

### Étape 7 : archiver l'atelier

```bash
gh repo archive nyaama-abdoucaba/pestel-nexus-brain-atelier
```

`gh` demande une confirmation.

Retour arrière : bouton « Unarchive this repository » dans les paramètres du
dépôt sur GitHub.

## Les cas d'erreur prévus

| Symptôme | Cause probable | Réaction |
|---|---|---|
| `git push` refusé à l'étape 1 | l'atelier a reçu un commit d'ailleurs | `git pull --rebase origin main`, puis repousser |
| `gh repo create` répond que le nom existe | l'étape 4 n'a pas abouti | vérifier avec `gh repo list`, refaire l'étape 4 |
| la pile Docker démarre sur une base vide | le dossier a changé de nom | vérifier `pwd`, le chemin doit rester identique |

## Critères d'acceptation

1. `gh repo view nyaama-abdoucaba/pestel-nexus-brain --json visibility` renvoie `PUBLIC`.
2. `git log --oneline | wc -l` renvoie `1` dans le dossier local.
3. `gh repo view nyaama-abdoucaba/pestel-nexus-brain-atelier --json isArchived` renvoie `true`.
4. `git --git-dir=../pestel-nexus-brain-atelier.git remote get-url origin` se termine par `-atelier.git`.
5. `./scripts/verify.sh` passe, 109 tests réussis.
6. Le contrôle `git grep` de l'étape 3 ne liste aucun fichier nominatif.

## Hors périmètre

- Installation de l'application GitHub Claude et du secret : lot L2b.
- Protection de la branche `main` sur la vitrine : à décider dans CCAR-001.
- Suppression des branches `claude/*` : elles restent dans l'atelier, sans travail propre.
