# Pestel Nexus Brain

> Runtime Python explicite pour préparer des commentaires LinkedIn ancrés dans des posts déjà collectés.

Ce dépôt ne publie rien sur LinkedIn. Il reçoit un post déjà stocké dans PostgreSQL, décide s’il mérite un commentaire, rédige une proposition, applique des règles déterministes, puis demande une décision à un juge LLM. Le résultat est sauvegardé pour revue humaine ou orchestration externe.

## État actuel

Le dépôt est volontairement recentré sur un seul produit : le **LinkedIn Comment Runtime**.

- Python 3.12, FastAPI et Pydantic pour l’API et les contrats.
- PostgreSQL est la seule base de données applicative.
- Ollama est appelé localement par le client natif `/api/chat` avec sortie structurée JSON Schema. Le transport compatible Anthropic reste disponible comme option de secours.
- n8n reste hors de ce dépôt : il peut collecter des posts, déclencher l’API et produire un digest, mais ne porte aucune logique de prompt ni de décision éditoriale.
- L’interface Streamlit sert aujourd’hui à consulter et gérer les cibles et posts ; elle ne pilote pas encore les runs de commentaires.

Le chemin actif ne dépend pas de CrewAI, Bedrock, DynamoDB, AgentCore ni Serper.

## Le flux de bout en bout

```text
n8n ou autre collecteur
        |
        v
PostgreSQL : linkedin_posts
        |
        v
POST /v1/linkedin-comment-runs
        |
        +--> Analyseur LLM : commenter ou ignorer + tags
        |
        +--> Présélection Python : corpus x tags x monde lecteur
        |      (zéro candidat : skip si le monde vend, mode question sinon)
        |
        +--> Sélecteur LLM : choisit un ancrage fermé
        |
        +--> Rédacteur LLM : brouillon ancré
        |
        +--> Contrôles Python : règles mécaniques
        |
        +--> Judge LLM : approuver, réécrire ou rejeter
                    |
                    +--> PostgreSQL : linkedin_comment_runs
                    +--> draft / skip / error
```

Les rôles sont séparés afin que chaque décision soit explicable :

1. **Analyseur** — détecte `fr` ou `en`, classe le type de post, propose des tags de situation, puis décide `commentable` ou `skip`.
2. **Présélection** — filtre par code le corpus d’ancrages selon les tags et le `reader_world`, avec trois candidats maximum.
3. **Sélecteur** — choisit un identifiant parmi ces candidats, ou `aucun`.
4. **Rédacteur** — reçoit le post, le principe choisi, l’ancrage choisi et les retours précis d’une tentative précédente. Il renvoie un objet JSON, pas du texte libre.
5. **Contrôles** — sans appel LLM, valident la langue, la structure, l’ancrage, le doublon, les liens et les formes faibles.
6. **Judge** — examine uniquement un brouillon passé aux contrôles. Il renvoie `approve`, `rewrite` avec des consignes concrètes, ou `reject`.

Un post ignoré par l’analyseur ne passe pas dans les étapes suivantes. Un commentaire devient `draft` seulement si les contrôles et le judge passent. Un contrat modèle cassé devient `error`, jamais un `skip` silencieux.

## Architecture du code

```text
app/
├── main.py                                      # application FastAPI et routes de santé
├── config.py                                    # configuration lue depuis l’environnement
├── linkedin_comments/
│   ├── contracts.py                              # modèles Pydantic et issues
│   ├── controls.py                               # validations déterministes
│   ├── corpus.py / corpus.json                   # magasin d'ancrages
│   ├── prompts.py                                # prompts versionnés lcr-v2
│   ├── ollama_client.py                          # client Ollama natif
│   ├── ollama_anthropic.py                       # transport optionnel compatible Anthropic
│   └── runtime.py                                # boucle analyse → sélection → écriture → judge
├── application/use_cases/
│   └── run_linkedin_comment.py                   # assemblage des dépendances du runtime
├── infrastructure/postgres/
│   └── linkedin_comment_repository.py            # lecture du post et sauvegarde du run
├── infrastructure/observability/logging.py       # logs JSON
└── interfaces/api/
    └── routes_linkedin_comment_runs.py           # endpoint HTTP du runtime

db/
├── init/                                        # schéma PostgreSQL, appliqué à l’initialisation
├── migrations/                                  # ajustements explicites pour bases existantes
└── seeds/                                       # jeu de données facultatif

ui/                                              # interface Streamlit de consultation
scripts/stack.sh                                 # aide de démarrage des services locaux
docker-compose.db.yml                            # PostgreSQL + pgAdmin
tests/linkedin_comments/                         # tests du runtime actif
```

Il n’y a pas d’agent généraliste, de mémoire cachée ou d’outil LLM. `LinkedInCommentRuntime` est l’orchestrateur unique et son code se lit linéairement dans [`app/linkedin_comments/runtime.py`](app/linkedin_comments/runtime.py).

## Contrats et décisions

### Entrée HTTP

```json
{
  "linkedin_post_id": "uuid-du-post",
  "reader_world": "icp1",
  "budget": {
    "max_total_tokens": 6000,
    "max_duration_seconds": 120
  }
}
```

`reader_world` est obligatoire et doit figurer dans le registre `app/linkedin_comments/worlds.py`. Un monde inconnu produit une `error` avec le code `monde_lecteur_inconnu`, jamais un `skip` silencieux. `budget` est facultatif et ne pilote plus le nombre de réécritures ; la boucle autorise un brouillon initial et une seule réécriture.

### Les mondes de lecteur et leurs deux régimes

Le registre porte les deux rôles commerciaux de la doctrine, et ils n'appellent pas le même moteur.

| Monde | Rôle | Anti-actualité IA | Question du juge |
| --- | --- | --- | --- |
| `icp1`, `icp1bis`, `dev` | vendre | active | apporte-t-il quelque chose au lecteur ? |
| `ai_practitioner` | se faire voir | coupée | l'auteur aurait-il envie de répondre ? |

Aucun monde n'exige une preuve vécue pour commenter. Un ancrage est une matière parmi d'autres, jamais une condition : le champ `comment_mode` vaut `ancre` quand une expérience vérifiée a été injectée, `libre` sinon.

Le rédacteur reçoit dans tous les cas le **regard** d'Abdoulaye, les domaines de `profil.py` filtrés pour ce monde, et choisit librement son mouvement. Aucune structure n'est imposée par type de post.

Le garde-fou contre le vécu fabriqué est la première question du juge, et elle est éliminatoire.

### Sortie

Chaque exécution retourne et sauvegarde :

- l’identifiant du run et du post ;
- une issue finale ;
- la langue détectée ;
- l’analyse, le choix d’ancrage et le monde lecteur ;
- chaque version de brouillon ;
- le résultat des contrôles et du judge pour chaque version ;
- les diagnostics finaux ;
- le modèle et la version du prompt.

Les issues finales sont :

| Issue | Signification |
| --- | --- |
| `draft` | Commentaire validé automatiquement, à relire avant toute publication. |
| `skip` | Le post ne mérite pas de commentaire, aucun ancrage n’est disponible ou le juge a rejeté. |
| `error` | Une dépendance, un budget d’exécution ou un contrat LLM a échoué. |

### Règles de contrôle

Les contrôles Python valident notamment :

- les objets déjà validés par Pydantic et la présence des champs utiles ;
- un commentaire non vide et dans une longueur utilisable ;
- la langue imposée par l’analyse ;
- la présence exacte d’un principe et d’un ancrage, en mode ancré ;
- la compatibilité de l’ancrage avec le `reader_world`, en mode ancré ;
- la fin sur une question directe et au plus une phrase affirmative, en mode question ;
- l’absence de commentaire identique lors de la même exécution ;
- la cohérence des diagnostics et des états.

Une violation de contrôle est traduite en consigne rédigée avant d’atteindre le rédacteur, par `controls.py::explain_violation` : il reçoit « Une phrase dépasse 20 mots. Coupe-la en deux ou raccourcis-la. », pas le code `sentence_too_long:2:28`. Les retours du judge sont préfixés `juge:`. Le rédacteur n’a donc jamais la consigne vague « améliore le texte », ni un code machine qu’il ne peut pas interpréter.

## Modèle et paramètres LLM

Le client par défaut est dans [`app/linkedin_comments/ollama_client.py`](app/linkedin_comments/ollama_client.py). Avant le premier appel, il vérifie qu’Ollama répond sur `/api/tags`, puis appelle `/api/chat` avec le JSON Schema attendu dans le champ `format`.

Le transport [`app/linkedin_comments/ollama_anthropic.py`](app/linkedin_comments/ollama_anthropic.py) reste disponible via `LLM_TRANSPORT=anthropic_compat`, mais le chemin natif `LLM_TRANSPORT=ollama_native` est la référence.

| Rôle | Température | Budget de sortie par défaut |
| --- | ---: | ---: |
| Analyseur | 0,1 | 1 200 tokens |
| Sélecteur | 0,0 | 200 tokens |
| Rédacteur | 0,5 | 700 tokens |
| Judge | 0,0 | 800 tokens |

Ces valeurs sont des points de départ. Elles doivent être calibrées sur un corpus annoté, en versionnant le prompt, le modèle, les décisions et les temps de réponse.

## Base de données

Le schéma créé par `db/init/` contient cinq tables applicatives.

| Table | Rôle |
| --- | --- |
| `target_categories` | Référentiel de catégories de profils. |
| `linkedin_targets` | Profils LinkedIn suivis et leur état de collecte. |
| `linkedin_target_categories` | Association plusieurs-à-plusieurs entre profils et catégories. |
| `linkedin_posts` | Posts collectés, normalisés et dédupliqués. |
| `linkedin_comment_runs` | Historique complet des décisions et brouillons du runtime. |

### Relations

```text
target_categories  ←── linkedin_target_categories ──→  linkedin_targets
                                                          |
                                                          └── linkedin_posts
                                                                  |
                                                                  └── linkedin_comment_runs
```

### Colonnes importantes

`linkedin_targets` contient notamment `id`, `name`, `linkedin_url` unique, `status`, `scrape_enabled`, `metadata`, `created_at` et `updated_at`.

`linkedin_posts` conserve le texte, l’URL unique, le profil source, les dates de publication et d’observation, la charge brute, ainsi que les données de déduplication : URL canonique, texte normalisé, hash, clé canonique et dates de première/dernière vue. Une contrainte et un trigger empêchent de garder des doublons logiques.

`linkedin_comment_runs` contient `linkedin_post_id`, `status`, `source_language`, `comment_text`, `analysis_payload`, `revisions_payload`, `diagnostics`, `model_name`, `prompt_version` et `created_at`. La colonne `status` conserve son nom historique mais stocke maintenant l’issue runtime : `draft`, `skip` ou `error`. Les objets riches restent en JSONB pour que le journal de décision soit conservé sans perte.

`db/init/` sert aux bases neuves. `db/migrations/` contient les ajustements à appliquer explicitement aux bases existantes ; ne pas rejouer aveuglément tout `db/init/` sur des données utiles.

Le fichier `db/seeds/001_ai_practitioners.sql` est un jeu de départ optionnel ; il n’est pas chargé automatiquement.

## API

Une fois l’application démarrée :

| Méthode | Chemin | Usage |
| --- | --- | --- |
| `GET` | `/health` | Santé simple du service. |
| `GET` | `/ping` | Alias léger de santé. |
| `POST` | `/v1/linkedin-comment-runs` | Lance une exécution pour un post existant. |

Réponses d’erreur attendues pour le endpoint de run :

- `404` : le post demandé n’existe pas ;
- `422` : la requête n’est pas conforme au contrat ;
- `503` : PostgreSQL ou Ollama n’est pas disponible.

Le traitement est actuellement synchrone : l’appel HTTP attend la fin de l’analyse, des éventuelles réécritures et du judge. Il est adapté à un volume modéré et à une orchestration simple ; un worker ou une file n’existe pas encore.

### Lire un run sans interpréter une boîte noire

La ligne `linkedin_comment_runs` est le journal de vérité : `analysis_payload` explique le tri initial, `revisions_payload` contient chaque brouillon et chaque verdict, et `diagnostics` explique la sortie finale. Pour investiguer une qualité faible, commencer dans cet ordre :

1. vérifier la décision, les tags et le `post_type` de l’analyse ;
2. vérifier le `selected_id` et l’ancrage associé dans le corpus ;
3. lire le premier brouillon et les violations éventuelles des contrôles ;
4. lire les raisons et instructions du judge ;
5. comparer le nombre de tentatives au budget demandé ;
6. seulement ensuite modifier le prompt, les contrôles ou les paramètres.

Cette séquence évite de confondre un mauvais ancrage d’entrée, une contrainte mécanique et un problème de rédaction.

## Démarrage local

### Prérequis

- Python 3.12 ;
- PostgreSQL local ;
- Ollama démarré sur la machine ;
- le modèle `gemma4:31b-cloud` disponible dans Ollama.

### Configuration

Copier `.env.example` vers `.env`, puis renseigner au minimum la connexion PostgreSQL. Les variables optionnelles sont :

```dotenv
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=gemma4:31b-cloud
OLLAMA_TIMEOUT_SECONDS=60
LLM_TRANSPORT=ollama_native
OLLAMA_THINK=
COMMENT_ANALYSIS_MAX_TOKENS=1200
COMMENT_SELECTOR_MAX_TOKENS=200
COMMENT_WRITER_MAX_TOKENS=700
COMMENT_JUDGE_MAX_TOKENS=800
LOG_LEVEL=INFO
```

Ne pas versionner `.env` : il contient les paramètres locaux de connexion.

### Installer et lancer l’API

```bash
cd /Users/abdoulaye/pestel-local/pestel-nexus-brain
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
./.venv/bin/uvicorn app.main:app --reload --port 8000
```

Vérifier ensuite `http://localhost:8000/health`. FastAPI expose également une documentation interactive sur `http://localhost:8000/docs`.

### Base locale et interface

`docker-compose.db.yml` démarre PostgreSQL et pgAdmin. Il s’appuie sur le réseau Docker externe `pestel_shared`, créé par `scripts/stack.sh` si nécessaire.

```bash
./scripts/stack.sh
```

Le script coordonne les services locaux de la stack. n8n reste dans le dépôt frère `../n8n` et Ollama reste un service de la machine ; ni l’un ni l’autre n’est embarqué dans l’image de l’API.

Pour lancer l’interface de consultation :

```bash
./.venv/bin/streamlit run ui/app.py
```

## n8n : frontière volontairement mince

n8n a trois responsabilités possibles :

1. collecter et enregistrer les posts dans `linkedin_posts` ;
2. appeler `POST /v1/linkedin-comment-runs` pour un identifiant de post ;
3. distribuer un digest ou une notification des résultats.

Il ne doit pas contenir les prompts, le contrôle de langue, les règles de validation, les décisions de qualité ou la boucle de réécriture. Ces décisions appartiennent au runtime Python afin qu’elles soient testables, versionnées et rejouables.

## Tests et vérification

Les tests actifs du runtime se trouvent dans `tests/linkedin_comments/`. Ils simulent le client LLM : aucun test n’envoie de requête à Ollama et aucun test ne génère de commentaire réel.

Commande de référence :

```bash
./.venv/bin/pytest tests -q
```

Avant de modifier prompts, contrôles ou contrats, ajouter un cas de test qui fixe le comportement attendu : langue, ancrage, raison de réécriture ou issue finale. Les tests du runtime couvrent en particulier le chemin d’approbation, le `skip` d’entrée, les violations des contrôles, les réécritures du judge et les erreurs de contrat.

## Calibration : comment avancer sans boîte noire

La calibration ne consiste pas à changer un prompt au hasard. Constituer d’abord un corpus de posts avec une décision humaine attendue : ignorer, commenter ou mettre en revue. Pour chaque essai, conserver :

- l’identifiant du post ;
- la version du prompt ;
- le modèle et les paramètres ;
- l’analyse et ses preuves ;
- le nombre de tentatives ;
- le verdict final ;
- les remarques humaines.

Comparer ensuite le respect de la langue, la validité JSON, la qualité de l’ancrage, la stabilité des verdicts, le nombre de boucles et la durée. Ne modifier qu’une variable à la fois, puis enregistrer le résultat. La version de prompt actuelle est `lcr-v2`.

## Limites connues et prochaines étapes

- Les runs sont synchrones ; il n’y a pas encore de file, de worker ni de reprise automatique.
- Le runtime ne collecte pas les posts et ne publie aucun commentaire.
- L’interface Streamlit ne présente pas encore la revue des `linkedin_comment_runs`.
- Les métriques sont principalement des logs JSON ; il n’y a pas encore de tableau de bord de qualité ou de coût.
- Le comptage de budget s’appuie sur les tokens de sortie fournis par le client ; il faut l’enrichir si un suivi fin de consommation devient nécessaire.
- Les migrations demandent une discipline de versionnage avant tout déploiement partagé ou de production.

## Documents complémentaires

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — contexte d’architecture plus large.
- [`docs/DOMAIN_CONTEXT.md`](docs/DOMAIN_CONTEXT.md) — vocabulaire et contexte métier.
- [`tasks/epics/2026-08-31-epic-linkedin-comment-runtime.md`](tasks/epics/2026-08-31-epic-linkedin-comment-runtime.md) — intention et slices de transformation, si le fichier est conservé dans votre arbre de travail.

## Principes de contribution

1. Garder l’orchestration lisible : pas d’agent implicite, pas de second chemin de décision caché.
2. Faire passer tout changement de contrat par Pydantic et les tests.
3. Conserver les décisions et diagnostics nécessaires à la revue humaine.
4. Préserver la frontière : collecte/digest dans n8n, intelligence éditoriale dans Python.
5. Ne jamais faire de publication LinkedIn sans une étape d’autorisation humaine explicite.
