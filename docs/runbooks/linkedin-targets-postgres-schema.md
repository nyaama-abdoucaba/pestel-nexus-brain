# Schéma PostgreSQL — cibles et posts LinkedIn

Ce schéma modélise les personnes choisies manuellement pour être suivies sur
LinkedIn et les posts collectés par le scraper Apify. Il remplace les anciennes
tables `practitioners` et `practitioner_posts`.

## Tables

Trois fichiers d'init créent le schéma dans l'ordre suivant :

```text
db/init/
  001_extensions.sql       — pgcrypto + trigger touch_updated_at
  010_linkedin_targets.sql — cibles, catégories, associations
  020_linkedin_posts.sql   — posts LinkedIn
```

### `target_categories`

Catalogue des catégories disponibles.

| Colonne | Type | Rôle |
|---|---|---|
| `slug` | `text` PK | Identifiant technique, ex. `ai_practitioner` |
| `label` | `text` | Libellé UI, ex. `Praticien IA` |
| `description` | `text` | Définition fonctionnelle |
| `created_at` | `timestamptz` | Date de création |

Contrainte : `slug` doit correspondre à `^[a-z][a-z0-9_]*$`.

### `linkedin_targets`

Une ligne = une personne choisie pour être suivie.

| Colonne | Type | Rôle |
|---|---|---|
| `id` | `uuid` PK | Généré par `gen_random_uuid()` |
| `name` | `text` | Nom affiché |
| `linkedin_url` | `text` UNIQUE | URL canonique normalisée |
| `why_follow` | `text` | Justification humaine du suivi |
| `status` | `text` | `candidate`, `active`, `paused`, `rejected` |
| `scrape_enabled` | `boolean` | Autorise le scraping automatique |
| `last_scraped_at` | `timestamptz` | Dernier passage Apify |
| `metadata` | `jsonb` | Attributs optionnels non structurants |
| `created_at` | `timestamptz` | Date de création |
| `updated_at` | `timestamptz` | Mis à jour automatiquement par trigger |

Contraintes :
- `linkedin_url` doit correspondre à `^https://www\.linkedin\.com/in/[^/?#]+$`
- `status` limité aux quatre valeurs ci-dessus
- `scrape_enabled = false` et `status = 'candidate'` par défaut

Index notables :
- `linkedin_targets_status_idx` — filtrage par statut
- `linkedin_targets_scrape_ready_idx` — index partiel sur `last_scraped_at`
  pour les cibles `active` et `scrape_enabled = true`

### `linkedin_target_categories`

Association plusieurs-à-plusieurs entre cibles et catégories.

| Colonne | Type | Rôle |
|---|---|---|
| `linkedin_target_id` | `uuid` FK | → `linkedin_targets.id` ON DELETE CASCADE |
| `category_slug` | `text` FK | → `target_categories.slug` ON DELETE CASCADE |
| `created_at` | `timestamptz` | Date d'association |

Clé primaire : `(linkedin_target_id, category_slug)`.

### `linkedin_posts`

Une ligne = un post LinkedIn collecté pour une cible suivie.

| Colonne | Type | Rôle |
|---|---|---|
| `id` | `uuid` PK | Généré par `gen_random_uuid()` |
| `linkedin_target_id` | `uuid` FK | → `linkedin_targets.id` ON DELETE RESTRICT |
| `url` | `text` UNIQUE | URL canonique du post |
| `text` | `text` | Texte collecté |
| `posted_at` | `timestamptz` | Date de publication (peut être `NULL`) |
| `observed_at` | `timestamptz` | Première observation, `now()` par défaut |
| `status` | `text` | `observed`, `selected`, `commented`, `skipped` |
| `raw_payload` | `jsonb` | Payload brut du scraper |
| `created_at` | `timestamptz` | Date de création |
| `updated_at` | `timestamptz` | Mis à jour automatiquement par trigger |

Contraintes :
- `url` doit correspondre à `^https://www\.linkedin\.com/.+`
- `text` non vide
- `status = 'observed'` par défaut
- FK vers `linkedin_targets` avec `ON DELETE RESTRICT` (supprimer une cible
  nécessite de vider ses posts d'abord)

Index notables :
- `linkedin_posts_target_posted_idx` sur `(linkedin_target_id, posted_at DESC)`
- `linkedin_posts_status_idx`
- `linkedin_posts_observed_idx`

## Démarrage

Si le volume PostgreSQL est vide, les scripts `db/init/` s'appliquent
automatiquement au premier démarrage :

```bash
cp .env.example .env
docker compose --env-file .env -f docker-compose.db.yml up -d
```

Accès PostgreSQL : `postgresql://pestel:pestel_dev_password@localhost:5432/pestel`

Accès pgAdmin : `http://localhost:5050`
(dans pgAdmin, hôte = `pestel-postgres`, port = `5432`)

## Charger le seed

Le répertoire `db/seeds/` n'est pas monté dans `/docker-entrypoint-initdb.d`.
Il faut l'exécuter explicitement après démarrage :

```bash
docker compose --env-file .env -f docker-compose.db.yml exec -T pestel-postgres \
  psql -v ON_ERROR_STOP=1 -U pestel -d pestel \
  < db/seeds/001_ai_practitioners.sql
```

Le seed est idempotent : le rejouer une deuxième fois ne crée pas de doublon.

## Si le volume existe déjà

Les scripts `db/init/` ne se rejouent pas sur un volume déjà initialisé.
Pour appliquer une évolution de schéma, l'exécuter manuellement via `psql`
ou pgAdmin, ou recréer le volume entièrement :

```bash
docker compose --env-file .env -f docker-compose.db.yml down -v
docker compose --env-file .env -f docker-compose.db.yml up -d
```

`down -v` supprime définitivement le volume et toutes les données locales.

## Contrôles après initialisation

```sql
-- Catégories disponibles
SELECT * FROM target_categories ORDER BY slug;

-- URL dupliquées (doit être vide)
SELECT linkedin_url, count(*)
FROM linkedin_targets
GROUP BY linkedin_url
HAVING count(*) > 1;

-- Cibles sans catégorie
SELECT t.id, t.name
FROM linkedin_targets t
LEFT JOIN linkedin_target_categories tc ON tc.linkedin_target_id = t.id
WHERE tc.linkedin_target_id IS NULL;

-- Répartition par statut et scraping
SELECT status, scrape_enabled, count(*)
FROM linkedin_targets
GROUP BY status, scrape_enabled
ORDER BY status, scrape_enabled;
```
