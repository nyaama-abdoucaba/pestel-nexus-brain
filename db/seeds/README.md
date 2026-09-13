# Seeds

Un seed remplit la base de données créée par `db/init/`. Aucun seed ne s'exécute
automatiquement : `docker-compose.db.yml` ne monte que `db/init/`.

## Ce qui vit ici

| Fichier | Contenu |
|---|---|
| `001_ai_practitioner_category.sql` | la catégorie `ai_practitioner` et sa description |
| `002_target_categories.sql` | les six catégories métier des cibles LinkedIn |
| `002_visibility_family_b_candidates.sql.example` | trois cibles inventées, montre la structure attendue |

## Ce qui n'y vit pas

Les cibles réelles nomment des personnes existantes et portent des appréciations
privées dans la colonne `why_follow`. Elles ont quitté le dépôt le 2026-09-10.

Emplacement local : `../donnees-privees/db-seeds/`, à côté du dépôt et hors de
tout suivi Git.

## Exécuter un seed

```bash
psql "$DATABASE_URL" -f db/seeds/001_ai_practitioner_category.sql
psql "$DATABASE_URL" -f db/seeds/002_target_categories.sql
psql "$DATABASE_URL" -f ../donnees-privees/db-seeds/001_ai_practitioners.sql
psql "$DATABASE_URL" -f ../donnees-privees/db-seeds/002_visibility_family_b_candidates.sql
```

L'ordre compte : les catégories doivent exister avant les cibles qui les
référencent. Les deux premières commandes vivent dans le dépôt, les deux
suivantes non.

## La règle

Un fichier de ce dossier qui nomme une personne réelle n'a rien à faire dans le
dépôt. Le schéma décrit la forme, les données remplissent la forme. La forme
voyage avec le code, le contenu non.
