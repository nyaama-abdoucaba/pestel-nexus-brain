# Preuves

Les mesures qui appuient une slice ou un spike. Un sous-dossier par code, par
exemple `ccar-000/`.

## Ce qui vit ici

Les preuves sans donnée nominative : constats de revue de code, tableaux de
mesure agrégés, résultats de spike, décomptes avant et après.

## Ce qui n'y vit jamais

Les sorties de run du moteur de commentaires. Elles contiennent de vrais posts
LinkedIn, avec le nom et l'URL de leur auteur.

Emplacement : `../donnees-privees/evidence/<code>/`, à côté du dépôt et hors de
tout suivi Git. Les preuves de LCR-015, LCR-016 et LCR-019 y ont été déplacées
le 2026-09-13.

La slice en markdown résume la mesure en chiffres et renvoie vers ce chemin.
Elle peut citer un extrait de post, jamais son auteur.

## La limite de cette règle

`.gitignore` ne lit pas le contenu d'un fichier, il lit son chemin. Rien
n'empêche techniquement un JSON nominatif d'entrer ici. Le contrôle se fait avant
chaque commit :

```bash
git grep -lE "author_name|linkedin\.com/(in|posts)" -- tasks/ ':!tasks/evidence/README.md'
```

La commande ne doit rien afficher.

Une mesure sans son échantillon et sans sa date ne prouve rien. Les deux se
notent dans le fichier ou dans le nom du sous-dossier.
