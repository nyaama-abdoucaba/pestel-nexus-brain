# PRD : aligner pestel-nexus-brain sur la certification CCAR-F

## 1. Contrôle du document

| Champ | Valeur |
|---|---|
| Titre | Alignement de `pestel-nexus-brain` sur les cinq domaines du CCAR-F |
| Code | CCAR |
| Version | 1.2 |
| Date | 2026-09-13 |
| Auteur | Abdoulaye, avec Claude Code |
| Statut | arbitré, prêt pour le lot 0 (décisions en section 12) |
| Source normative | Claude Certified Architect Foundations, Exam Guide v1.0, juillet 2026 |
| Dépôt cible | `/Users/abdoulaye/pestel-local/pestel-nexus-brain` |
| Epic | `tasks/epics/2026-09-13-epic-ccar.md` |

### Historique des versions

| Version | Date | Changement |
|---|---|---|
| 1.0 | 2026-09-09 | première rédaction, domaines 1, 3, 4 et 5 |
| 1.1 | 2026-09-10 | domaine 2 intégré, revue en deux voies, décisions Q1 à Q5 |
| 1.2 | 2026-09-13 | point 12.2 tranché : dépôt atelier archivé, vitrine publique neuve. Lot L0 redéfini |

## 2. Résumé exécutif

Ce document décrit comment transformer `pestel-nexus-brain` en support de révision
pour l'examen CCAR-F, sans casser le moteur de commentaires qui tourne aujourd'hui.

L'idée directrice tient en une phrase. Le dépôt couvre déjà bien la sortie
structurée et la validation, il ne couvre presque pas la boucle agentique, les
outils MCP, la configuration Claude Code et la revue de code. Le plan comble ces
trous par trois ajouts : une voie agentique dans `app/agents/`, un serveur MCP
`pestel-mcp`, et une couche de configuration dans `.claude/`. Le fichier
`runtime.py` reste le chemin de production et ne bouge pas.

Quatre résultats sortent de ce travail. Abdoulaye révise sur son propre code, ce
qui ancre mieux qu'un cours. Claude Code accède enfin à la base par des outils
nommés. Le projet gagne une revue de code sur ses PR. Le juge éditorial voit sa
justesse mesurée pour la première fois.

## 3. Contexte et problème

### 3.1 Ce que fait le projet aujourd'hui

Le trajet de référence, déjà documenté dans `CLAUDE.md` :

```text
n8n -> interfaces/api -> application/use_cases -> linkedin_comments/runtime.py
    -> worlds . profil . prompts . controls . contracts
    -> infrastructure/postgres -> JSON renvoyé à n8n
```

`runtime.py` enchaîne trois appels modèle dans un ordre fixe : analyseur, puis
rédacteur, puis juge. Les contrôles Python s'intercalent entre le rédacteur et le
juge. La boucle de réécriture est bornée à une tentative par `MAX_ATTEMPTS`.

Le moteur parle à un modèle local via Ollama. Deux transports coexistent déjà,
choisis par `LLM_TRANSPORT` dans `app/config.py` :

| Transport | Module | Structure garantie par |
|---|---|---|
| `ollama_native` | `ollama_client.py` | champ `format` d'Ollama, JSON Schema en contrainte de décodage |
| `anthropic_compat` | `ollama_anthropic.py` | `tool_use` sur l'endpoint `/v1/messages` |

### 3.2 L'écart avec l'examen

L'examen note 60 questions sur cinq domaines. Abdoulaye retient les cinq domaines,
soit la totalité des points. Le domaine 2 est entré au périmètre le 2026-09-10.

| Domaine | Poids | Couverture actuelle du dépôt | Écart |
|---|---:|---|---|
| 1. Architecture agentique et orchestration | 27 % | faible | boucle sur `stop_reason`, coordinateur, sous-agents, hooks, sessions |
| 2. Design d'outils et MCP | 18 % | faible | aucun serveur MCP propre au projet, descriptions d'outils jamais mesurées |
| 3. Configuration Claude Code et workflows | 20 % | faible | `.claude/rules/`, `.claude/commands/`, skills mal placées, aucune revue sur les PR |
| 4. Prompt engineering et sortie structurée | 20 % | forte | `tool_choice`, lots, exemples few-shot documentés, scores de confiance |
| 5. Contexte et fiabilité | 15 % | moyenne | escalade explicite, erreurs structurées, calibration humaine |

Le détail des écarts par exigence figure en section 9.

### 3.3 Le problème formulé

Abdoulaye ne peut pas réviser les domaines 1 et 3 sur ce dépôt. Le code n'expose
aucune boucle agentique et aucune configuration Claude Code digne de ce nom. Il
révise donc sur de la lecture, ce qui tient mal face à des questions de jugement
en situation.

## 4. Objectifs

### 4.1 Objectifs produit

1. Rendre chaque objectif d'examen des cinq domaines observable dans le dépôt.
2. Livrer une revue de code qui tourne en local et publie ses constats sur une vraie PR.
3. Ne dégrader ni la disponibilité ni la qualité du moteur de commentaires.
4. Garder le tout exécutable hors ligne, sur inférence Ollama, avec bascule vers Claude.

### 4.2 Objectifs d'apprentissage

Chaque exigence de la section 9 se rattache à un énoncé de tâche de l'examen.
La table de traçabilité en annexe A permet de réviser domaine par domaine.

### 4.3 Hors périmètre

| Exclusion | Raison |
|---|---|
| Le serveur MCP n8n comme support du domaine 2 | ses outils décrivent des nœuds et des exécutions, pas le métier d'Abdoulaye |
| Toute modification du code de n8n | décision d'Abdoulaye du 2026-09-10 |
| Outils MCP en écriture sur la base | un outil qui écrit met en jeu les données de production, aucun besoin de révision ne l'exige |
| Réécriture de `runtime.py` en système agentique | risque de production, voir section 10.2 |
| Déploiement ou hébergement de serveurs MCP | déclaré hors examen par le guide |
| Fine-tuning, RLHF, caching de prompts | déclarés hors examen par le guide |
| Passage du moteur de production à Claude payant | aucun besoin exprimé |

## 5. Indicateurs de succès

| Indicateur | Mesure | Cible |
|---|---|---|
| Couverture des objectifs | énoncés de tâche couverts par un artefact du dépôt | 30 sur 30, tous domaines |
| Revue utilisable | temps entre l'ouverture de la PR et les constats publiés | moins de 3 minutes sur une PR de 5 fichiers |
| Recouvrement des deux voies | constats trouvés par une voie et manqués par l'autre, sur 3 PR | mesuré et écrit, sert à décider si une voie suffit |
| Faux positifs de la revue | constats rejetés par Abdoulaye sur 20 constats | moins de 5 sur 20 |
| Non-régression | `./scripts/verify.sh` | vert avant et après chaque lot |
| Boucle agentique prouvée | test qui compte les tours et vérifie `stop_reason` | présent et vert |
| Justesse du juge mesurée | accord entre le juge et Abdoulaye sur 30 commentaires | mesuré et écrit, pas de cible imposée |
| Aiguillage des outils MCP | requêtes routées vers le bon outil sur 10 demandes ambiguës | mesuré avant et après réécriture des descriptions |

## 6. Utilisateurs et cas d'usage

Un seul utilisateur : Abdoulaye, consultant, à la fois auteur du dépôt et candidat.

| Cas d'usage | Déclencheur | Résultat attendu |
|---|---|---|
| Réviser un domaine | une session de révision | ouvrir la table de traçabilité, lire le code, lancer la commande associée |
| Vérifier une tranche | fin d'une tranche de travail | revue locale, constats classés, décision de commit |
| Comparer deux versions de prompt | doute sur une évolution éditoriale | deux sessions forkées depuis une analyse commune, résultats côte à côte |
| Escalader un post difficile | le juge rejette deux fois, ou la politique est muette | le run sort en revue humaine, avec un dossier de reprise |

## 7. Étude de faisabilité technique

Cette section répond à la question posée : Ollama parle-t-il l'API Messages, et le
Claude Agent SDK tourne-t-il dessus. La réponse est oui pour les deux, avec des
trous précis qu'il faut connaître.

### 7.1 Ollama et l'API Messages

Ollama expose `/v1/messages` depuis la version 0.14. La documentation officielle
liste ce qui passe et ce qui ne passe pas.

| Élément de l'API Messages | Ollama | Effet sur la révision |
|---|---|---|
| `model`, `max_tokens`, `messages` | supporté | boucle agentique testable en local |
| blocs `tool_use` et `tool_result` | supporté | le cœur du domaine 1.1 est jouable |
| `system`, `stream`, `temperature`, `top_p`, `top_k`, `stop_sequences` | supporté | rien à signaler |
| `tools` | supporté | outils déclarés avec JSON Schema, domaine 4.3 partiel |
| `thinking` | supporté | utile sur les modèles à raisonnement |
| `stop_reason` en réponse | supporté | la condition d'arrêt de l'examen existe vraiment |
| `usage` en réponse | supporté | budget de contexte mesurable, domaine 5.1 |
| `tool_choice` | absent | impossible de forcer un outil, voir 7.3 |
| `metadata` | absent | sans effet ici |
| `/v1/messages/count_tokens` | absent | compter les tokens passe par `usage` après coup |
| Caching de prompts | absent | hors examen de toute façon |
| API Batches | absent | le domaine 4.5 se révise par simulation, voir 9.4 |
| Citations et PDF | absent | sans effet ici |

Le module `ollama_anthropic.py` documente déjà ces limites. Le PRD les reprend
parce qu'elles décident du périmètre jouable.

### 7.2 Ollama et le Claude Agent SDK

Le SDK Python `claude-agent-sdk` lance le binaire `claude` sous le capot. Ce binaire
lit `ANTHROPIC_BASE_URL` et `ANTHROPIC_AUTH_TOKEN`. Ollama documente cette
configuration et fournit même un raccourci, `ollama launch claude`.

Le SDK expose un champ `env` dans `ClaudeAgentOptions`, fusionné par-dessus
l'environnement du processus. La bascule se fait donc par exécution, sans variable
globale :

```python
from claude_agent_sdk import ClaudeAgentOptions

options = ClaudeAgentOptions(
    env={
        "ANTHROPIC_BASE_URL": "http://localhost:11434",
        "ANTHROPIC_AUTH_TOKEN": "ollama",
    },
    model="qwen3-coder",
)
```

Conséquence pratique. Les sous-agents, les hooks, les sessions et les serveurs MCP
sont exécutés par le binaire `claude`, pas par le fournisseur du modèle. Ces
mécanismes fonctionnent donc sur Ollama. Ce qui change, c'est la qualité du
raisonnement du modèle, pas la disponibilité de la mécanique.

Versions constatées sur la machine le 2026-09-09 : `ollama` 0.23.2 et `claude`
2.1.260. Le service Ollama ne tournait pas au moment du relevé.

### 7.3 Le trou `tool_choice`, et pourquoi il sert la révision

L'examen teste `tool_choice` avec trois valeurs : `auto`, `any` et la sélection
forcée d'un outil nommé. Ollama ignore ce paramètre. Une exécution locale ne peut
donc pas prouver la garantie.

Ce trou reste utile pédagogiquement. Le dépôt possède les deux garanties côte à
côte : le champ `format` d'Ollama contraint le décodage, alors que `tool_use` sans
`tool_choice` ne contraint rien. Un diagnostic exécutable montre la différence, sur
le modèle du script existant `check_ollama_format.py`. Comprendre pourquoi
`format` tient et pourquoi `tool_use` seul lâche vaut mieux qu'une définition apprise.

Une bascule vers l'API Claude reste possible pour les exercices qui exigent
`tool_choice`. Elle coûte une variable d'environnement et quelques appels payants.

### 7.4 Ce que la faisabilité impose au plan

| Contrainte | Décision d'architecture |
|---|---|
| Pas de `tool_choice` sur Ollama | garantie de structure par `format` en production, `tool_use` en voie agentique, écart documenté et testé |
| Pas d'API Batches | lot simulé en local, avec `custom_id` et relance des seuls échecs |
| Qualité de raisonnement variable en local | la revue de code accepte deux moteurs, choisis par variable d'environnement |
| Le SDK lance le binaire `claude` | une seule configuration `.claude/` sert la ligne de commande et le SDK |

## 8. Architecture cible

```text
                    ┌── production, inchangée ──────────────────────────┐
n8n -> interfaces/api -> use_cases -> linkedin_comments/runtime.py -> PG
                    └───────────────────────────────────────────────────┘
                                    │ réutilise
                                    ▼
                        contracts . prompts . controls . worlds . profil
                                    ▲
                    ┌───────────────┴── voie agentique, nouvelle ───────┐
    app/agents/loop.py  ->  coordinateur  ->  sous-agents  ->  hooks
    (stop_reason)           (hub)             (contexte explicite)  (garde-fous)
                    └───────────────────────────────────────────────────┘

    .claude/            rules/ . commands/ . skills/ . agents/ . settings.json
    scripts/review.sh   revue locale, deux passes, sortie JSON schématisée
```

Trois principes tiennent cette découpe.

Les contrats restent partagés. `contracts.py` décrit les mêmes objets pour les deux
voies. Un changement de schéma casse les deux, ce qui se voit tout de suite.

La production ne dépend jamais de la voie agentique. `runtime.py` n'importe rien de
`app/agents/`. La dépendance va dans l'autre sens.

La configuration `.claude/` sert les deux usages. Le binaire `claude` en ligne de
commande et le SDK lisent les mêmes fichiers, via `setting_sources`.

## 9. Exigences fonctionnelles

Chaque exigence porte un code, une priorité et un critère d'acceptation vérifiable.
Priorités : `M` pour indispensable, `S` pour souhaitable, `C` pour confort.

### 9.1 Domaine 1, architecture agentique et orchestration

| Code | Exigence | Pri. | Critère d'acceptation |
|---|---|---|---|
| F-1.1 | Écrire une boucle agentique dans `app/agents/loop.py` qui continue tant que `stop_reason` vaut `tool_use` et s'arrête sur `end_turn` | M | un test injecte un faux client qui renvoie `tool_use` puis `end_turn`, et vérifie deux tours, un bloc `tool_result` ajouté, aucun plafond d'itération comme condition d'arrêt principale |
| F-1.2 | Construire un coordinateur en étoile qui délègue à `analyste`, `redacteur`, `juge` | M | tout échange entre sous-agents passe par le coordinateur, un test vérifie qu'aucun sous-agent n'en appelle un autre |
| F-1.3 | Passer le contexte aux sous-agents dans leur prompt, jamais par héritage implicite | M | le prompt du rédacteur contient l'analyse complète, un test compare la charge utile attendue et celle envoyée |
| F-1.4 | Poser une barrière programmatique qui bloque `publier_commentaire` tant que le juge n'a pas rendu `approve` | M | un hook `PreToolUse` refuse l'appel, un test prouve le refus même quand le prompt demande de publier |
| F-1.5 | Normaliser les formats hétérogènes par un hook `PostToolUse` | S | les dates Apify, Postgres et Unix ressortent en ISO 8601, test sur les trois formats |
| F-1.6 | Documenter le choix entre chaîne fixe et décomposition dynamique | S | une note dans `docs/decisions/` explique pourquoi le commentaire garde une chaîne fixe et pourquoi l'audit de feed adapte ses sous-tâches |
| F-1.7 | Utiliser les sessions nommées et `fork_session` pour comparer deux versions de prompt | S | un script forke une analyse commune, lance deux rédacteurs, écrit les deux résultats dans `tasks/evidence/` |

Précision sur F-1.4. Le refus doit être programmatique, pas une consigne de prompt.
C'est exactement la distinction que l'examen teste sur le cas du remboursement.

### 9.2 Domaine 2, design d'outils et intégration MCP

Le support de ce domaine est un serveur MCP local, `pestel-mcp`, qui expose le
cerveau Pestel en lecture seule. Aujourd'hui, Claude Code ne voit pas la base :
il écrit du SQL à l'aveugle, ou Abdoulaye colle des résultats à la main.

Quatre outils, calqués sur les tables existantes.

| Outil | Rend | Source |
|---|---|---|
| `chercher_cible` | une ligne de `linkedin_targets`, dont `why_follow` | table `linkedin_targets` |
| `lire_post` | le texte du post et ses métadonnées utiles | table des posts LinkedIn |
| `lister_runs` | les runs d'un post, filtrables par statut et par date | table `linkedin_comment_runs` |
| `expliquer_run` | la trace complète d'un run : analyse, révisions, verdicts | `revisions_payload` et `model_calls` |

Deux ressources MCP complètent l'ensemble : `pestel://mondes`, lue depuis
`worlds.py`, et `pestel://domaines`, lue depuis `profil.py`. Une ressource sert de
catalogue et évite les appels d'exploration.

| Code | Exigence | Pri. | Critère d'acceptation |
|---|---|---|---|
| F-2.1 | Mesurer l'aiguillage entre `lire_post` et `expliquer_run`, d'abord avec des descriptions minimales, puis après réécriture | M | dix demandes ambiguës passées avant et après, taux de bon aiguillage écrit dans `tasks/evidence/`, progression constatée |
| F-2.2 | Renvoyer des erreurs structurées portant `errorCategory`, `isRetryable` et un texte lisible | M | trois cas testés : Postgres éteint donne `transient` relançable, UUID malformé donne `validation` non relançable, post sans run donne un résultat vide et aucune erreur |
| F-2.3 | Restreindre les outils de chaque sous-agent à son rôle | M | le rédacteur accède à `chercher_cible`, le juge non, un test vérifie le refus |
| F-2.4 | Déclarer le serveur dans `.mcp.json` au niveau projet, avec expansion de variable | M | le fichier contient `${DATABASE_URL}`, aucun secret n'entre dans Git, un second serveur personnel vit dans `~/.claude.json` et les deux répondent en même temps |
| F-2.5 | Écrire la règle de choix entre outils natifs et outils MCP | S | une note explique quand `Grep` suffit et quand `expliquer_run` gagne, avec un exemple de chaque |

Précision sur F-2.1. Le recouvrement entre `lire_post` et `expliquer_run` est
voulu. Les deux renvoient « des informations sur un post », ce qui reproduit
exactement le piège de la question 2 de l'examen. La mesure avant et après
transforme une définition apprise en résultat constaté.

Précision sur F-2.2. Le troisième cas porte la vraie difficulté. Un post sans run
n'est pas une panne : c'est une requête réussie sans correspondance. L'examen teste
cette distinction, et un serveur qui la rate fait relancer l'agent pour rien.

Précision sur le périmètre. Aucun outil n'écrit en base. Cette limite protège les
données de production et suffit à couvrir les cinq énoncés du domaine.

### 9.3 Domaine 3, configuration Claude Code et workflows

| Code | Exigence | Pri. | Critère d'acceptation |
|---|---|---|---|
| F-3.1 | Découper `CLAUDE.md` en règles thématiques importées par `@import` | M | le fichier racine tient en une page, les règles vivent dans `.claude/rules/`, `/memory` montre la hiérarchie chargée |
| F-3.2 | Créer des commandes de projet dans `.claude/commands/` | M | `/verify`, `/slice`, `/revue-locale` et `/dry-run` existent, sont versionnées, et s'exécutent |
| F-3.3 | Déplacer les skills vers `.claude/skills/` avec frontmatter complet | M | chaque `SKILL.md` porte `context: fork`, `allowed-tools` et `argument-hint`, une skill verbeuse ne pollue plus la session principale |
| F-3.4 | Écrire des règles conditionnées par chemin dans `.claude/rules/` | M | un fichier avec `paths: ["app/linkedin_comments/**"]` ne se charge qu'en éditant ces fichiers, vérifié par `/memory` |
| F-3.5 | Écrire la règle de choix entre plan mode et exécution directe | S | une note liste trois tâches passées et le mode qui aurait convenu, avec la raison |
| F-3.6 | Écrire le script de revue maison, lancé à la main, moteur Ollama par défaut | M | voir section 9.6.3 |
| F-3.7 | Installer l'action officielle de revue, moteur Claude, déclenchée à chaque PR | M | voir section 9.6.4, constats publiés en commentaires en ligne sur une vraie PR |

Note sur l'état constaté. Les skills vivent aujourd'hui dans `/skills`, hors de
`.claude/`, et `.claude/skills/README.md` renvoie vers ce dossier. Claude Code ne
charge donc pas ces skills comme des skills. Le frontmatter actuel n'utilise ni
`context: fork` ni `allowed-tools`, qui sont deux points d'examen.

Autre point constaté. Le fichier `CLAUDE.md` à la racine commence par le titre
`# AGENTS.md`, et son contenu double `docs/AGENTS.md`. Le découpage de F-3.1
résout cette duplication.

### 9.4 Domaine 4, prompt engineering et sortie structurée

| Code | Exigence | Pri. | Critère d'acceptation |
|---|---|---|---|
| F-4.1 | Écrire des critères de revue catégoriels, jamais des consignes de prudence | M | le prompt de revue liste ce qui se signale et ce qui se tait, aucune formule du type « sois conservateur » |
| F-4.2 | Constituer un catalogue d'exemples few-shot pour les cas ambigus | M | au moins quatre exemples : post de célébration, post anglais d'un auteur français, post porteur d'injection, post sans matière |
| F-4.3 | Prouver la sortie structurée par `tool_use` et par `format`, et documenter l'écart | M | `check_anthropic_compat.py` mesure le taux de réponses conformes des deux transports sur vingt posts, résultat écrit dans `tasks/evidence/` |
| F-4.4 | Distinguer les erreurs que la relance corrige de celles qu'elle ne corrige pas | M | la relance transporte l'erreur de validation, un test prouve qu'une information absente de la source ne déclenche pas de relance |
| F-4.5 | Simuler un traitement par lots avec `custom_id` | S | un script traite cent posts, relance les seuls `custom_id` en échec, écrit une note sur le choix entre appel synchrone et lot |
| F-4.6 | Revoir en plusieurs passes et par instance indépendante | M | la revue analyse chaque fichier seul, puis fait une passe croisée, dans une session distincte de celle qui a écrit le code |

Précision sur F-4.4. L'examen insiste sur cette distinction. Une erreur de format se
corrige par relance avec le message de validation. Une information absente du
document source ne se corrige jamais par relance.

### 9.5 Domaine 5, contexte et fiabilité

| Code | Exigence | Pri. | Critère d'acceptation |
|---|---|---|---|
| F-5.1 | Élaguer les sorties d'outil avant leur accumulation en contexte | M | le chargement d'un post ne transmet que les champs utiles, un test compte les champs transmis |
| F-5.2 | Définir des critères d'escalade explicites vers Abdoulaye | M | un run sort en revue humaine sur trois déclencheurs nommés, jamais sur un score de confiance auto-déclaré |
| F-5.3 | Structurer les erreurs avec catégorie, caractère relançable et résultat partiel | M | `llm_errors.py` porte `errorCategory` et `isRetryable`, le coordinateur décide sur ces champs, test par catégorie |
| F-5.4 | Persister les constats dans des fichiers bloc-notes lors des explorations longues | S | une exploration de code écrit ses constats dans `tasks/evidence/`, et la session suivante les relit |
| F-5.5 | Mesurer la justesse du juge par échantillonnage stratifié | S | trente commentaires tirés par `post_type`, accord ou désaccord noté, taux par type écrit dans une note |
| F-5.6 | Conserver le lien entre affirmation et source dans les sorties | S | `passage_le_plus_proche` existe déjà sur `JudgeResult`, l'étendre au rédacteur et au dossier d'escalade |

Précision sur F-5.2. L'examen rejette explicitement l'escalade fondée sur un score
de confiance auto-déclaré par le modèle. Les déclencheurs proposés sont : le juge
rejette deux fois, la politique éditoriale ne dit rien du cas, le moteur n'avance
plus. Abdoulaye tranche cette liste, voir Q3 en section 12.

### 9.6 La revue de code, cœur du domaine 3.6

Le dépôt possède un dépôt GitHub distant, `nyaama-abdoucaba/pestel-nexus-brain`,
déjà configuré comme `origin`. Rien n'est à simuler. Les branches, les PR et les
commentaires de revue en ligne existent, il suffit de reprendre le fil.

Cette section remplace la règle actuelle du dépôt, qui interdit branches et PR.
Le travail passe désormais par une branche par tranche, puis une PR.

#### 9.6.1 L'abonnement couvre les deux voies

Le compte d'Abdoulaye est connecté via claude.ai, avec un abonnement `pro`.
Cet abonnement paie la revue dans les deux cas, et aucune clé d'API n'est requise.

Sur la machine, `claude -p` utilise la session déjà ouverte. Rien à configurer.

Dans GitHub Actions, la commande `claude setup-token` fabrique un jeton longue
durée adossé à l'abonnement. Ce jeton se dépose en secret de dépôt sous le nom
`CLAUDE_CODE_OAUTH_TOKEN`, et l'action officielle l'utilise à la place d'une clé
d'API. La documentation est explicite : avec un jeton OAuth, les exécutions passent
sur l'abonnement, pas sur la facturation à l'usage. Les plans Pro, Max, Team et
Enterprise sont couverts.

Ce jeton reste nominatif. Il porte l'abonnement d'Abdoulaye, pas celui du dépôt.
Le jour où quelqu'un d'autre pousse du code, il faudra une clé d'API partagée.

Ce qui reste à la charge d'Abdoulaye : les minutes GitHub Actions, comptées sur son
plan GitHub. Un dépôt privé consomme un quota mensuel, un dépôt public ne consomme
rien.

#### 9.6.2 Deux voies, deux rôles

| | Voie A, script maison | Voie B, action officielle |
|---|---|---|
| Où ça tourne | le Mac d'Abdoulaye | machine GitHub |
| Moteur par défaut | Ollama, en local | Claude, via l'abonnement |
| Déclenchement | commande lancée à la main | automatique à chaque PR |
| Coût | aucun | minutes GitHub, usage de l'abonnement |
| Rôle | l'exercice du domaine 3.6 | le filet de sécurité |

Les deux voies cohabitent, avec des rôles séparés. La voie A fait manipuler les
drapeaux que l'examen cite nommément, ce qu'une action clé en main n'apprend pas.
La voie B tourne toute seule et rattrape ce que la voie A ne verra pas, parce
qu'Abdoulaye aura oublié de la lancer.

Une note sur le runner auto-hébergé, écarté. Il ne servirait qu'à faire tourner
Ollama sur une machine GitHub. Puisque la voie B utilise Claude, cette
installation ne se justifie plus.

#### 9.6.3 Voie A, le script maison

```bash
scripts/review.sh --pr 12
```

Le script enchaîne cinq étapes.

1. Il récupère le diff de la PR avec `gh pr diff 12`.
2. Il lance une passe par fichier, en session indépendante, avec `claude -p` et un
   schéma de sortie. Chaque passe ne voit qu'un fichier, ce qui évite la dilution
   d'attention que l'examen décrit.
3. Il lance une passe croisée sur l'ensemble des diffs, dédiée aux flux entre
   fichiers.
4. Il fusionne les constats et écrit `tasks/evidence/revue-pr-12.json`.
5. Il publie les constats sur la PR avec `gh pr comment`, puis sort en code 1 si un
   constat bloquant subsiste.

La commande de base, avec les drapeaux que l'examen cite nommément :

```bash
claude -p "$(cat .claude/prompts/revue-fichier.md)" \
  --output-format json \
  --json-schema .claude/schemas/constats.json \
  --append-system-prompt "Tu relis un seul fichier. Ne signale rien qui dépasse ce fichier."
```

Les drapeaux `-p`, `--output-format`, `--json-schema`, `--resume`, `--fork-session`
et `--agents` existent bien dans la version installée, 2.1.260. Ce point a été
vérifié sur la machine le 2026-09-09.

Une relance de revue après de nouveaux commits ne doit pas republier les mêmes
constats. Le script relit `tasks/evidence/revue-pr-12.json` et le passe en contexte,
avec la consigne de ne signaler que ce qui est nouveau ou toujours ouvert. L'examen
teste ce point précis.

Le moteur se change par une seule variable. `REVUE_MOTEUR=ollama` est le défaut et
pose `ANTHROPIC_BASE_URL` vers le service local. `REVUE_MOTEUR=claude` bascule sur
l'abonnement. Comparer les deux moteurs sur la même PR est un exercice d'examen à
part entière.

#### 9.6.4 Voie B, l'action officielle

La commande `/install-github-app`, lancée depuis Claude Code dans le dépôt, fait
trois choses. Elle installe l'application GitHub, elle crée le secret
d'authentification, et elle ouvre la PR qui pose les fichiers de workflow.

Le workflow de revue tient en peu de lignes. L'argument `--comment` décide de la
destination : sans lui, les constats restent dans le journal d'exécution.

```yaml
name: Code Review
on:
  pull_request:
    types: [opened, synchronize, ready_for_review, reopened]
jobs:
  review:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: read
      issues: read
      id-token: write
    steps:
      - uses: actions/checkout@v6
      - uses: anthropics/claude-code-action@v1
        with:
          claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
          plugin_marketplaces: "https://github.com/anthropics/claude-code.git"
          plugins: "code-review@claude-code-plugins"
          prompt: "/code-review:code-review --comment ${{ github.repository }}/pull/${{ github.event.pull_request.number }}"
          claude_args: '--allowedTools "mcp__github_inline_comment__create_inline_comment"'
```

Deux réglages bornent la consommation. `--max-turns` limite le nombre de tours, et
un délai d'expiration au niveau du travail évite les exécutions folles. Le plan Pro
supporte mal une revue sur une PR de quarante fichiers, ce qui plaide pour des
tranches courtes.

## 10. Plan de livraison

### 10.1 Lots

| Lot | Contenu | Domaines | Durée estimée | Dépend de |
|---|---|---|---|---|
| L0 | Atelier et vitrine : archiver le dépôt privé, publier un dépôt neuf sans données personnelles | 3 | une heure | rien, préalables faits le 2026-09-13 |
| L1 | Configuration `.claude/` : règles, commandes, skills déplacées | 3 | une demi-journée | L0 |
| L2 | Revue voie A : script maison, prompts, schémas, publication par `gh pr comment` | 3, 4 | une journée | L1 |
| L2b | Revue voie B : `claude setup-token`, secret, workflow de l'action officielle | 3 | une heure | L0 |
| L3 | Serveur `pestel-mcp` : quatre outils, deux ressources, erreurs structurées | 2 | une journée | L1 |
| L4 | Boucle agentique et coordinateur dans `app/agents/` | 1, 2 | une à deux journées | L3 |
| L5 | Hooks : barrière avant publication, normalisation des formats | 1 | une demi-journée | L4 |
| L6 | Fiabilité : erreurs structurées, escalade, élagage du contexte | 5 | une journée | L4 |
| L7 | Mesure : lots simulés, échantillonnage du juge, aiguillage des outils | 2, 4, 5 | une journée | L2, L6 |

Le lot 3 passe avant le lot 4 pour une raison de dépendance. Les sous-agents du
coordinateur ont besoin d'outils à se répartir. Sans serveur MCP, l'exigence F-2.3
n'a rien à distribuer.

Chaque lot suit la règle du dépôt. Une spec dans `tasks/specs/`, une tranche dans
`tasks/slices/`, une vérification par `./scripts/verify.sh`, une mise à jour de
`tasks/WEEKLY.md` et `tasks/BACKLOG.md`. Ces dossiers ont été réorganisés sous
`tasks/archives/` le 2026-09-10, hors de ce PRD : le lot 1 rétablit une arborescence
de travail claire.

### 10.2 Pourquoi `runtime.py` ne bouge pas

Réécrire la chaîne de production en système agentique coûterait de la fiabilité.
La chaîne actuelle est déterministe, rapide et testée sans base ni modèle, grâce
aux deux `Protocol` de `runtime.py`. Un coordinateur agentique introduit du
non-déterminisme dans un moteur qui produit du texte publié sous le nom d'Abdoulaye.

La voie `app/agents/` réutilise les mêmes contrats et les mêmes prompts. Elle sert
la révision et l'expérimentation. Si elle se révèle meilleure sur trente posts, la
bascule devient une décision fondée sur des mesures, pas un pari.

## 11. Risques

| Risque | Effet | Probabilité | Mitigation |
|---|---|---|---|
| Le modèle local relit mal le code | revue bruyante, confiance perdue | élevée | double moteur, mesure du taux de faux positifs dès le lot 2 |
| La voie agentique dérive de la production | deux moteurs éditoriaux divergents | moyenne | contrats partagés, aucun import de `app/agents/` dans `runtime.py` |
| `tool_choice` absent fausse la révision | mauvaise réponse le jour de l'examen | moyenne | diagnostic écrit qui montre l'écart, fiche de révision dédiée |
| Le temps de révision passe en développement | l'examen approche sans révision | moyenne | chaque lot livre un artefact révisable, pas seulement du code |
| Le dépôt public expose des données personnelles | tiers identifiables publiés sans leur accord | faible depuis le 2026-09-13 | données sorties du dépôt, histoire neuve, contrôle `git grep` avant chaque commit |
| La revue publiée sur la PR ralentit le travail | contournement systématique | faible | passe par fichier limitée au diff, sortie en moins de trois minutes |
| Ollama évolue et casse la couche de compatibilité | voie hors ligne indisponible | faible | version d'Ollama épinglée dans la note d'installation, diagnostic exécutable |

## 12. Décisions

### 12.1 Décisions arrêtées le 2026-09-10

| Point | Décision | Conséquence dans ce document |
|---|---|---|
| Périmètre | le domaine 2 entre au périmètre, les cinq domaines sont couverts | sections 3.2, 4.3, 9.2, annexe A |
| Support du domaine 2 | un serveur MCP propre au projet, pas le serveur MCP n8n | section 9.2 |
| Code de n8n | aucune modification | section 4.3 |
| Frontière de revue | de vraies branches et de vraies PR sur GitHub, la simulation est abandonnée | section 9.6, lot L0 |
| Moteur de revue | les deux voies coexistent : script maison sur Ollama, action officielle sur Claude | section 9.6 |
| Facturation de la revue | l'abonnement Pro couvre les deux voies, aucune clé d'API | section 9.6.1 |
| Escalade | trois déclencheurs : le juge rejette deux fois, la politique est muette, le moteur n'avance plus | exigence F-5.2 |
| Ordre des lots | L0 à L7 tels qu'écrits | section 10.1 |
| Visibilité du dépôt | passage en public voulu par Abdoulaye | section 12.2 |
| Méthode de publication | dépôt neuf, l'ancien renommé `pestel-nexus-brain-atelier` puis archivé | section 12.2, lot L0 |
| Nom de la vitrine | `pestel-nexus-brain` | section 12.2 |
| Preuves de run | hors du dépôt, dans `../donnees-privees/evidence/` | `tasks/evidence/README.md` |

### 12.2 Décision du 2026-09-13 : les données personnelles avant le passage en public

Point ouvert en version 1.1, tranché en version 1.2.

Le constat de départ. Le dépôt suivait des fichiers qui nommaient des personnes
réelles, avec des appréciations privées. Aucun code ne les lisait : les tests
travaillent sur des identités fictives.

Ce qui a été fait avant le lot L0 :

| Élément | Traitement |
|---|---|
| `sourcing_linkedin.csv`, `Annuaire Profiles Juin 2926.md` | sortis vers `../donnees-privees/sourcing/` |
| `db/imports/2026-09-02-linkedin-targets/` | sorti vers `../donnees-privees/db-imports/` |
| seeds `001` et `002` | coupés en deux : les catégories restent, les 18 et 31 cibles nommées sortent |
| preuves de LCR-015, LCR-016, LCR-019 | sorties vers `../donnees-privees/evidence/` |
| un nom d'auteur dans `tasks/RESTE-A-FAIRE-COMMENTAIRES-ICP1.md` | anonymisé |
| `.gitignore` | règles ajoutées pour empêcher le retour de ces fichiers |

Ce que ces gestes ne règlent pas : l'historique. Les commits d'avril et de
septembre contiennent toujours les fichiers. D'où la décision.

| Option | Retenue | Raison |
|---|---|---|
| Garder le dépôt privé | non | Abdoulaye veut une vitrine publique |
| Réécrire l'historique | non | 30 commits non poussés, risque de casse élevé |
| Dépôt neuf, ancien archivé | oui | vitrine propre, atelier intact et figé, un seul dépôt actif |

L'archivage corrige un coût annoncé en version 1.1, « deux dépôts à suivre ». Un
dépôt archivé passe en lecture seule, il ne demande aucun suivi.

L'exécution est décrite dans la spec du lot L0 :
`tasks/specs/2026-09-13-ccar-000-atelier-vitrine-spec.md`.

## Annexe A. Traçabilité

| Énoncé d'examen | Exigence | Artefact du dépôt |
|---|---|---|
| 1.1 Boucle agentique et `stop_reason` | F-1.1 | `app/agents/loop.py`, `tests/agents/test_loop.py` |
| 1.2 Coordinateur et sous-agents | F-1.2 | `app/agents/coordinator.py`, `.claude/agents/` |
| 1.3 Invocation, contexte, spawn | F-1.3 | prompts du coordinateur, tests de charge utile |
| 1.4 Barrières et passation | F-1.4 | hook `PreToolUse`, dossier d'escalade |
| 1.5 Hooks et normalisation | F-1.5 | hook `PostToolUse` |
| 1.6 Décomposition des tâches | F-1.6 | `docs/decisions/` |
| 1.7 Sessions, reprise, fork | F-1.7 | script de comparaison de prompts |
| 2.1 Descriptions et frontières d'outils | F-2.1 | `pestel-mcp`, mesure d'aiguillage dans `tasks/evidence/` |
| 2.2 Erreurs structurées MCP | F-2.2 | `pestel-mcp`, tests par catégorie d'erreur |
| 2.3 Distribution des outils et `tool_choice` | F-2.3 | définitions de sous-agents, test de refus |
| 2.4 Intégration MCP dans Claude Code | F-2.4 | `.mcp.json`, `~/.claude.json` |
| 2.5 Outils natifs | F-2.5 | note de choix entre `Grep` et outils MCP |
| 3.1 Hiérarchie `CLAUDE.md` | F-3.1 | `CLAUDE.md`, `.claude/rules/` |
| 3.2 Commandes et skills | F-3.2, F-3.3 | `.claude/commands/`, `.claude/skills/` |
| 3.3 Règles par chemin | F-3.4 | `.claude/rules/*.md` avec `paths` |
| 3.4 Plan mode contre exécution directe | F-3.5 | note de décision |
| 3.5 Raffinement itératif | F-4.2, F-4.4 | catalogue d'exemples, boucle de relance |
| 3.6 Claude Code en CI/CD | F-3.6 | `scripts/review.sh`, `gh pr diff`, `gh pr comment` |
| 3.6 Claude Code en CI/CD | F-3.7 | `.github/workflows/`, `CLAUDE_CODE_OAUTH_TOKEN` |
| 4.1 Critères explicites | F-4.1 | `.claude/prompts/revue-fichier.md` |
| 4.2 Few-shot | F-4.2 | `app/linkedin_comments/prompts.py` |
| 4.3 Sortie structurée par outil | F-4.3 | `ollama_anthropic.py`, `check_anthropic_compat.py` |
| 4.4 Validation et relance | F-4.4 | `runtime.py`, tests de relance |
| 4.5 Traitement par lots | F-4.5 | `scripts/batch_runs.py`, note de politique |
| 4.6 Revue multi-passes | F-4.6 | `scripts/review.sh` |
| 5.1 Gestion du contexte | F-5.1 | élagage au chargement du post |
| 5.2 Escalade et ambiguïté | F-5.2 | critères d'escalade, `RunOutcome` étendu |
| 5.3 Propagation des erreurs | F-5.3 | `llm_errors.py` |
| 5.4 Exploration de gros dépôts | F-5.4 | fichiers bloc-notes dans `tasks/evidence/` |
| 5.5 Revue humaine et calibration | F-5.5 | note d'échantillonnage |
| 5.6 Provenance et incertitude | F-5.6 | `JudgeResult.passage_le_plus_proche` |

## Annexe B. Sources

- Claude Certified Architect Foundations, Exam Guide v1.0, juillet 2026, fourni par Abdoulaye.
- Compatibilité Anthropic d'Ollama : https://docs.ollama.com/api/anthropic-compatibility
- Claude Code avec l'API Anthropic d'Ollama : https://ollama.com/blog/claude
- Référence Python du Claude Agent SDK : https://code.claude.com/docs/en/agent-sdk/python
- Claude Code dans GitHub Actions : https://code.claude.com/docs/en/github-actions
- Relevés machine du 2026-09-09 : `ollama` 0.23.2, `claude` 2.1.260, drapeaux CLI vérifiés par `claude --help`.
