# Guide de refonte du schéma PostgreSQL local

## 1. But

Ce guide prépare la remise à plat de PostgreSQL local. La base peut être recréée
depuis zéro : il n'est donc pas nécessaire de préserver le schéma expérimental
`practitioners` / `practitioner_posts` ni de construire une migration complexe.

Objectifs :

- modéliser des entités métier durables ;
- remplacer `practitioners` par des cibles LinkedIn catégorisables ;
- remplacer `practitioner_posts` par des posts LinkedIn généraux ;
- préparer la disparition de `source_items` sans recréer une table fourre-tout ;
- conserver un seed idempotent pour les praticiens IA sélectionnés ;
- rendre la remise à zéro et la vérification reproductibles.

Ce document décrit la cible. Les scripts SQL seront réécrits après validation des
arbitrages de la section 8.

## 2. Principes

### Nommer les entités stables

Une personne suivie reste une cible LinkedIn, qu'elle soit praticien IA, CxO,
prospect ou partenaire. La table canonique doit s'appeler `linkedin_targets`.

Une publication collectée reste un post LinkedIn quelle que soit la catégorie de
son auteur. La table canonique doit s'appeler `linkedin_posts`. Le nom `posts`
seul serait ambigu avec les contenus produits par Pestel Nexus.

### Ne pas créer une table par catégorie

Il faut éviter `practitioners`, `cxo_targets`, `prospects`, etc. Ces tables
dupliqueraient les mêmes colonnes et géreraient mal une personne appartenant à
plusieurs catégories.

### Garder les données structurantes hors de `jsonb`

Les champs utilisés pour filtrer, joindre, dédupliquer ou piloter un workflow ont
des colonnes explicites : URL, statut, catégorie, activation du scraping, dates et
état de revue. `metadata` et `raw_payload` restent réservés aux attributs souples.

### Utiliser des identifiants cohérents

Les tables principales utilisent des UUID. Les valeurs techniques utilisent
l'anglais, le singulier et le `snake_case` : `ai_practitioner`, `candidate`,
`active`, `paused`, `rejected`.

## 3. Schéma cible proposé

### `linkedin_targets`

Une ligne représente une personne ou un compte LinkedIn choisi pour être suivi.

| Colonne | Type indicatif | Rôle |
|---|---|---|
| `id` | `uuid` | Clé primaire interne |
| `name` | `text` | Nom affiché |
| `linkedin_url` | `text` | URL de profil normalisée et unique |
| `why_follow` | `text` | Justification humaine du suivi |
| `status` | `text` | `candidate`, `active`, `paused`, `rejected` |
| `scrape_enabled` | `boolean` | Autorise le scraping automatique |
| `last_scraped_at` | `timestamptz` | Dernier scraping terminé |
| `metadata` | `jsonb` | Attributs optionnels non structurants |
| `created_at` | `timestamptz` | Date de création |
| `updated_at` | `timestamptz` | Date de modification |

Contraintes recommandées : URL obligatoire et unique après normalisation,
contrainte sur le statut, `scrape_enabled=false` par défaut, index sur `status` et
index pour retrouver les cibles actives à scraper.

Le champ actuel `domain='ai'` n'est pas retenu. Il est redondant avec la catégorie
`ai_practitioner` et deviendrait ambigu pour une cible couvrant plusieurs sujets.

### `target_categories`

Catalogue documenté des catégories disponibles.

| Colonne | Type indicatif | Rôle |
|---|---|---|
| `slug` | `text` | PK, par exemple `ai_practitioner` |
| `label` | `text` | Libellé UI, par exemple `Praticien IA` |
| `description` | `text` | Définition fonctionnelle |
| `created_at` | `timestamptz` | Date de création |

### `linkedin_target_categories`

Association plusieurs-à-plusieurs entre cibles et catégories.

| Colonne | Type indicatif | Rôle |
|---|---|---|
| `linkedin_target_id` | `uuid` | FK vers `linkedin_targets.id` |
| `category_slug` | `text` | FK vers `target_categories.slug` |
| `created_at` | `timestamptz` | Date d'association |

La clé primaire est `(linkedin_target_id, category_slug)`. Les deux relations
utilisent `ON DELETE CASCADE`. Cette structure évite une migration future si une
même personne est à la fois CxO et praticien IA.

### `linkedin_posts`

Une ligne représente un post LinkedIn externe observé pour une cible suivie.

| Colonne | Type indicatif | Rôle |
|---|---|---|
| `id` | `uuid` | Clé primaire interne |
| `linkedin_target_id` | `uuid` | Auteur suivi |
| `url` | `text` | URL canonique unique du post |
| `text` | `text` | Texte collecté |
| `posted_at` | `timestamptz` | Date de publication |
| `observed_at` | `timestamptz` | Première observation |
| `status` | `text` | État de revue ou traitement |
| `raw_payload` | `jsonb` | Payload brut du scraper |
| `created_at` | `timestamptz` | Date de création |
| `updated_at` | `timestamptz` | Date de modification |

Contraintes recommandées : FK obligatoire vers la cible, URL unique, insertion
idempotente sur l'URL, index `(linkedin_target_id, posted_at desc)` et index sur
le statut.

Première proposition de statuts : `observed`, `selected`, `commented`, `skipped`.
Il ne faut pas ajouter d'états correspondant à des traitements encore inexistants.

## 4. Disparition de `source_items`

`source_items` mélange une abstraction technique d'ingestion avec plusieurs
réalités métier. Le remplacement ne doit pas être une autre table générique.

Règle : une donnée rejoint la table correspondant à ce qu'elle est, pas à la
manière dont elle est entrée dans le système.

| Donnée actuelle | Destination cible |
|---|---|
| Profil LinkedIn suivi | `linkedin_targets` |
| Catégorie de profil | `linkedin_target_categories` |
| Post LinkedIn d'une cible | `linkedin_posts` |
| Payload brut du scraper | `linkedin_posts.raw_payload` |
| Article ou signal RSS | Table métier dédiée à définir après inventaire |
| Texte destiné au RAG | Couche documentaire dérivée à redéfinir séparément |

Pour la première étape, `sources`, `source_items`, `documents` et `chunks` peuvent
être retirées du schéma initial si aucun flux local validé ne les utilise encore.
Si le RAG revient, ses tables devront référencer les entités canoniques sans les
remplacer.

## 5. Organisation des scripts SQL

Les fichiers de `db/init` ne s'exécutent automatiquement que sur un volume vide.
L'ordre doit être explicite :

```text
db/init/
  001_extensions.sql
  010_linkedin_targets.sql
  020_linkedin_posts.sql

db/seeds/
  001_ai_practitioners.sql
```

- `001_extensions.sql` active seulement les extensions réellement utilisées ;
- `010_linkedin_targets.sql` crée cibles, catégories et associations ;
- `020_linkedin_posts.sql` crée les posts et leurs index ;
- le seed contient les données, jamais le schéma.

`vector` ne doit pas être activé par réflexe. Il reviendra avec un chantier RAG
confirmé.

## 6. Réécriture du seed des praticiens IA

`db/seeds/001_ai_practitioners.sql` reste la source des personnes sélectionnées,
mais doit être adapté au nouveau modèle. Il devra :

1. créer ou mettre à jour la catégorie `ai_practitioner` ;
2. normaliser toutes les URLs LinkedIn de la même façon ;
3. faire un upsert dans `linkedin_targets` sur `linkedin_url` ;
4. récupérer l'UUID de chaque cible ;
5. insérer l'association de catégorie avec `ON CONFLICT DO NOTHING` ;
6. pouvoir être rejoué sans doublon ;
7. ne pas réactiver une cible mise en pause ou rejetée après le premier chargement.

L'upsert peut actualiser `name`, `why_follow` et les métadonnées de référence. Il
ne doit pas écraser `status`, `scrape_enabled` ou `last_scraped_at` lors d'un
rejeu.

## 7. Remise à zéro locale

### Préconditions

- confirmer qu'aucune donnée locale ne doit être conservée ;
- arrêter les applications et workflows qui écrivent dans PostgreSQL ;
- valider les nouveaux scripts SQL avant de supprimer le volume ;
- faire éventuellement un `pg_dump` de contrôle.

Depuis `pestel-nexus-brain` :

```bash
docker compose --env-file .env -f docker-compose.db.yml down -v
docker compose --env-file .env -f docker-compose.db.yml up -d
docker compose --env-file .env -f docker-compose.db.yml ps
```

Attention : `down -v` supprime définitivement le volume PostgreSQL du projet.

Le répertoire `db/seeds` n'est pas monté dans
`/docker-entrypoint-initdb.d`. Le seed doit être exécuté explicitement :

```bash
docker compose --env-file .env -f docker-compose.db.yml exec -T pestel-postgres \
  psql -v ON_ERROR_STOP=1 -U pestel -d pestel \
  < db/seeds/001_ai_practitioners.sql
```

Il doit ensuite être rejoué une seconde fois pour confirmer son idempotence.

## 8. Arbitrages avant implémentation

### Catégories multiples

Proposition : conserver `linkedin_target_categories`, même si le premier seed
n'utilise que `ai_practitioner`.

À confirmer : une cible pourra-t-elle appartenir à plusieurs catégories ?

### Statut des posts

Proposition : `observed`, `selected`, `commented`, `skipped`.

À confirmer : `selected` signifie-t-il seulement une validation humaine ou aussi
une mise en file pour génération de commentaire ?

### Données non-LinkedIn

À faire : inventorier les types réellement utiles de `source_items` avant de
concevoir leurs tables. Aucun remplacement générique ne sera créé par anticipation.

### Couche RAG

À confirmer : `documents`, `chunks` et `pgvector` restent-ils dans le prochain
schéma initial ou passent-ils dans un chantier séparé ?

## 9. Contrôles après initialisation

```sql
SELECT * FROM target_categories ORDER BY slug;

SELECT linkedin_url, count(*)
FROM linkedin_targets
GROUP BY linkedin_url
HAVING count(*) > 1;

SELECT t.id, t.name
FROM linkedin_targets AS t
LEFT JOIN linkedin_target_categories AS tc
  ON tc.linkedin_target_id = t.id
 AND tc.category_slug = 'ai_practitioner'
WHERE tc.linkedin_target_id IS NULL;

SELECT tc.*
FROM linkedin_target_categories AS tc
LEFT JOIN linkedin_targets AS t ON t.id = tc.linkedin_target_id
LEFT JOIN target_categories AS c ON c.slug = tc.category_slug
WHERE t.id IS NULL OR c.slug IS NULL;

SELECT status, scrape_enabled, count(*)
FROM linkedin_targets
GROUP BY status, scrape_enabled
ORDER BY status, scrape_enabled;
```

Résultats attendus : aucune URL dupliquée, aucune association orpheline, tous les
enregistrements du seed associés à `ai_practitioner`, aucune ligne supplémentaire
au second passage du seed et aucune nouvelle cible scrapée sans activation.

## 10. Ordre du chantier

1. Valider les arbitrages de la section 8.
2. Inventorier les données réellement utiles de `source_items`.
3. Rédiger l'epic de refonte PostgreSQL et UI.
4. Décliner l'epic en specs : schéma, seed, réseau Docker, accès PostgreSQL de
   l'UI, vue des cibles, puis vue des posts.
5. Réécrire `db/init` et le seed.
6. Ajouter les tests de contraintes et d'idempotence.
7. Réinitialiser le volume, charger le seed et effectuer les contrôles.
8. Adapter l'UI seulement après stabilisation du schéma.

