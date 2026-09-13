# Imports

Ce dossier accueillait les fichiers source bruts de qualification des cibles
LinkedIn, en CSV.

Ces fichiers nomment des personnes existantes. Ils ont quitté le dépôt le
2026-09-10 et vivent désormais dans `../donnees-privees/db-imports/`, à côté du
dépôt et hors de tout suivi Git.

Aucun code ne les lisait. Ils servaient à la qualification manuelle, avant
écriture du seed SQL correspondant.

Tout nouvel import de données nominatives suit la même règle : il reste hors du
dépôt. Voir `db/seeds/README.md`.
