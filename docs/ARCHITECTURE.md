# Architecture expliquée

Ce document remplace l'ancienne fiche technique. Il s'adresse à quelqu'un qui lit
le Python sans connaître les conventions des frameworks. Il se comprend seul.

**L'idée directrice : le cœur du moteur ne connaît ni la base de données, ni le
modèle de langage.** Tout le reste de la découpe découle de là.

---

## 1. Ce que fait ce dépôt

Une seule chose. Il reçoit l'identifiant d'un post LinkedIn déjà collecté, décide
s'il mérite un commentaire, en rédige un, le fait relire par un juge, puis rend
le résultat.

Il ne collecte rien. Il ne publie rien sur LinkedIn. La collecte et l'envoi du
digest par mail vivent dans n8n, hors de ce dépôt.

---

## 2. Les quatre couches

Plus on descend, moins le code connaît le monde extérieur.

```
app/
├── main.py                    la porte d'entrée HTTP
├── config.py                  les réglages, lus dans les variables d'environnement
│
├── interfaces/api/            COUCHE 1 : parler HTTP
│   └── routes_linkedin_comment_runs.py         22 lignes
│
├── application/use_cases/     COUCHE 2 : enchaîner les étapes
│   └── run_linkedin_comment.py                 32 lignes
│
├── linkedin_comments/         COUCHE 3 : le moteur
│   ├── runtime.py             l'orchestrateur              368 lignes
│   ├── prompts.py             les textes envoyés au modèle 302 lignes
│   ├── controls.py            les règles mécaniques        408 lignes
│   ├── contracts.py           la forme de toutes les données 172 lignes
│   ├── profil.py              les domaines et les principes
│   ├── worlds.py              le registre des mondes de lecteur
│   ├── ollama_client.py       le dialogue avec Ollama
│   └── dry_run.py             l'outil de test sur de vrais posts
│
└── infrastructure/            COUCHE 4 : les outils techniques
    ├── postgres/linkedin_comment_repository.py  82 lignes
    └── observability/logging.py                 24 lignes
```

Deux mots de vocabulaire, employés partout ensuite. **FastAPI** est la
bibliothèque qui transforme une fonction Python en adresse HTTP. **Pydantic** est
celle qui décrit la forme attendue d'une donnée et refuse tout ce qui n'y
correspond pas.

---

## 3. Le trajet d'une requête, fichier par fichier

Suivons un seul post, depuis n8n jusqu'au mail.

### n8n envoie

```
POST http://host.docker.internal:8000/v1/linkedin-comment-runs
{ "linkedin_post_id": "...", "reader_world": "ai_practitioner" }
```

### `app/main.py`

Le fichier que le conteneur lance. Il crée l'application FastAPI, branche le
journal en JSON, expose `/health` que Docker interroge pour dire « healthy », et
raccroche la route des commentaires. Aucune logique métier ici.

### `app/interfaces/api/routes_linkedin_comment_runs.py`

Vingt-deux lignes, et c'est voulu. Cette couche fait trois choses.

Elle vérifie que le corps reçu a la forme de `StartLinkedInCommentRun`, sinon
elle répond 422 sans rien exécuter. Elle appelle le cas d'usage. Elle traduit
trois exceptions métier en codes HTTP : post introuvable en 404, Ollama muet en
503, PostgreSQL muet en 503.

### `app/application/use_cases/run_linkedin_comment.py`

Le monteur. Il construit le dépôt PostgreSQL, charge le post, construit le client
Ollama, construit le moteur en lui passant les deux, puis lance. Il ne décide
rien, il assemble.

### `app/linkedin_comments/runtime.py`

Tout le travail, en six étapes.

| Étape | Ce qu'elle fait | Qui décide |
|---|---|---|
| 1 | le monde du lecteur existe-t-il dans le registre ? | code |
| 2 | analyseur : commentable, langue, post_type, domaines touchés | modèle |
| 3 | les domaines reconnus donnent leurs principes | code |
| 4 | rédacteur : le regard, les principes, les règles d'écriture, cinq exemples | modèle |
| 5 | contrôles : quatre règles objectives | code |
| 6 | juge : fabrication, platitude, valeur | modèle |

À chaque étape modèle, `runtime.py` demande son texte à `prompts.py`, l'envoie
via `ollama_client.py`, et valide la réponse contre un schéma de `contracts.py`.

Trois appels de modèle par post, pas quatre : le sélecteur d'ancrage a été
supprimé le 05/09/2026 après avoir refusé les candidats 27 fois sur 27.

La boucle autorise un brouillon et une seule réécriture. Ce nombre est fixé en
dur dans `MAX_ATTEMPTS`, il n'est pas configurable.

### `app/infrastructure/postgres/linkedin_comment_repository.py`

Écrit le résultat dans la table `linkedin_comment_runs`. Le résultat remonte
ensuite toute la chaîne et ressort en JSON. C'est ce JSON que le nœud
`Build Digest` de n8n met en forme dans le mail.

---

## 4. Le point qui explique toute la découpe

`runtime.py` ne connaît ni PostgreSQL ni Ollama. Il connaît deux contrats,
déclarés en haut du fichier :

```python
class CommentLlm(Protocol):
    model: str
    def healthcheck(self) -> None: ...
    def complete(self, *, system, user, max_tokens, temperature, schema) -> Completion: ...

class RunRepository(Protocol):
    def save(self, result: CommentRunResult) -> None: ...
```

Un `Protocol` en Python est une promesse de forme. Il dit « donne-moi n'importe
quel objet qui sait faire `save()` », sans exiger que ce soit PostgreSQL.

C'est exactement pour ça que le dry-run existe. Il passe au moteur un
`_NullRepository` dont le `save()` ne fait rien. Les tests lui passent un
`FakeLlm` qui rend des réponses écrites d'avance. Le moteur ne voit pas la
différence.

Sans cette découpe, tester une décision du juge exigerait une base de données et
un modèle qui tourne. Trente minutes par essai au lieu d'une demi-seconde.

C'est aussi pourquoi `llm_factory.py` existe. Il choisit entre deux clients
Ollama interchangeables selon la variable `LLM_TRANSPORT`, et le moteur ne sait
pas lequel il a reçu.

---

## 5. Les mondes de lecteur

Un monde répond à une seule question : qu'est-ce qu'on essaie de faire à ce
lecteur ? Ce n'est ni une liste de comptes, ni un persona.

C'est quatre réglages dans `worlds.py`, et rien d'autre.

| Réglage | Ce qu'il décide |
|---|---|
| `rejette_actualite` | commenter une actualité IA est opportuniste, ou c'est le sujet |
| `question_du_juge` | ce que le juge exige avant d'approuver |
| les `mondes` de `corpus.json` | quels ancrages ce lecteur a le droit de recevoir |
| les `mondes` de `profil.py` | quels domaines de son parcours éclairent ce lecteur |

Deux rôles commerciaux existent, `vendre` et `se_faire_voir`. Depuis le
05/09/2026, le rôle ne décide plus si l'on commente, seulement de la question que
le juge pose à la fin.

Aucun monde n'exige plus une preuve vécue pour commenter. Le réglage
`ancrage_requis` a été retiré : un ancrage est une matière parmi d'autres, jamais
une condition. Le résultat porte `comment_mode`, qui vaut `ancre` quand une
expérience vérifiée a été injectée, et `libre` sinon.

Le garde-fou contre le vécu fabriqué ne vit donc plus dans l'absence de
commentaire. Il est la première question du juge, et elle est éliminatoire :
attribuer à Abdoulaye une expérience qu'on ne lui a pas fournie fait rejeter le
brouillon quelle que soit sa qualité.

Un monde absent du registre produit une erreur `monde_lecteur_inconnu`. Jamais un
skip silencieux : une faute de frappe doit se voir.

### La différence entre un monde et une catégorie

Une catégorie est une donnée. C'est la liste des comptes suivis, dans la table
`target_categories` de PostgreSQL. Elle change chaque semaine sans toucher au
code.

Un monde est un comportement. Il change quel prompt part et quels contrôles
s'appliquent. Un comportement se relit, se teste et se versionne avec le code.

Plusieurs catégories partagent donc le même monde. La correspondance vit dans le
nœud `Config Categorie` de chaque workflow n8n, un workflow par catégorie.

---

## 6. Le regard, et les principes

Deux objets, dans `profil.py`, et la séparation est tout le dispositif.

Un **domaine** décrit ce que quinze ans de métier permettent de voir. Il
n'affirme rien, donc il n'a rien à prouver. Six domaines existent, chacun ouvert
à certains mondes seulement.

Un **principe** est transposable. Il s'applique à un post qu'Abdoulaye n'a jamais
vécu, sans lui prêter aucune expérience. Les douze principes sont répartis dans
les domaines : `politiques_publiques` porte p9 et p11, `ingenierie_ia` en porte
six. Un principe peut appartenir à plusieurs domaines.

La chaîne éditoriale se lit alors ainsi :

```
le post touche-t-il un de mes domaines ?
    oui  -> les principes de ces domaines sont proposés au rédacteur
            il en retient un, ou aucun
    non  -> il répond en conversation, sans principe
```

Le champ `comment_mode` du résultat vaut `principe` ou `conversation`.

Le corpus d'ancrages a été supprimé le 05/09/2026. Quinze faits datés ne
couvraient pas la diversité d'un fil d'actualité, et le sélecteur les refusait
27 fois sur 27. Énumérer une vie professionnelle dans une application est un
autre travail que celui de commenter.

---

## 7. Les trois issues, jamais confondues

| Issue | Signification |
|---|---|
| `draft` | un commentaire est prêt, à relire avant publication |
| `skip` | décision éditoriale : rien à dire, ou le juge a rejeté |
| `error` | panne : Ollama muet, PostgreSQL muet, contrat modèle cassé, monde inconnu |

Une erreur de contrat n'est pas une décision. Elle range sous `error`, jamais
sous `skip`. Sans cette règle, un feed pauvre et un moteur en panne deviennent
indiscernables dans les journaux.

---

## 8. Frontières

PostgreSQL est la seule persistance.

Ollama est le seul fournisseur de modèle, appelé par défaut sur `/api/chat` avec
un JSON Schema natif dans le champ `format`.

Un piège de configuration mérite d'être connu. Un modèle à raisonnement comme
`qwen3.5:9b` dépense tout son budget de sortie dans le champ `thinking` et
renvoie un `content` vide. Il faut `OLLAMA_THINK=false`. Vérifier avec
`python -m app.linkedin_comments.check_ollama_format` avant de changer de modèle.

n8n reste extérieur. Il collecte, déclenche et met en forme le digest. Il ne
porte aucune logique éditoriale.

Aucun agent, proxy distant ni stockage cloud ne fait partie de cette architecture.

---

## 9. Vérifier soi-même

Les tests, une demi-seconde, sans base ni modèle :

    ./.venv/bin/pytest tests -q

Le moteur sur de vrais posts archivés, avec le détail de chaque décision :

    OLLAMA_MODEL=qwen3.5:9b OLLAMA_THINK=false \
      ./.venv/bin/python -m app.linkedin_comments.dry_run \
      --world ai_practitioner --db --limit 12 --verbose

L'API en conteneur, de bout en bout :

    curl -s -X POST http://localhost:8000/v1/linkedin-comment-runs \
      -H 'Content-Type: application/json' \
      -d '{"linkedin_post_id":"<uuid>","reader_world":"ai_practitioner"}'

Un changement de code Python n'atteint le conteneur qu'après reconstruction de
l'image. `./scripts/stack.sh start` passe `--build` pour cette raison.
