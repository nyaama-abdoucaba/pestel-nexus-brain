# Commentaires ICP1 — état réel et travail restant

État au 5 septembre 2026. Document de reprise pour Abdoulaye et pour la prochaine session de développement.

**Le chantier n'est pas terminé.** Le code local a été modifié et les tests ciblés passent, mais les dernières consignes n'ont pas encore été évaluées avec le modèle réel. Le premier essai complet a produit **1 draft, 15 skips et 1 erreur sur 17 posts**. Ce résultat ne prouve pas que les commentaires sont acceptables pour ICP1.

## 1. Objectif à conserver

Produire des commentaires acceptables pour la cible ICP1 observée dans le feed consultant, avec un code ordonné, structuré et auditable, compatible avec le traitement futur d'autres cibles.

Le trajet reste :

```text
n8n : sélection des cibles, collecte et digest de relecture
  → FastAPI : réception de l'identifiant du post et du monde lecteur
  → cas d'usage : chargement du post et construction du runtime
  → runtime : analyse, expérience facultative, rédaction, contrôles et juge
  → PostgreSQL : historique des résultats et des décisions
  → réponse JSON à n8n
```

Objectif relationnel : se faire remarquer pour la qualité de l'échange, obtenir des réponses et faciliter les connexions. Un échange peut ensuite faire apparaître une occasion de DM. Une réponse polie ne suffit pas à qualifier un lead tiède.

Un `draft` reste un **brouillon à relire**. Aucun commentaire, DM ou email n'a été envoyé dans cette session. Les taux de réponse et d'acceptation ne peuvent pas être démontrés par un test local.

## 2. Orientation éditoriale retenue

- Partir du post, de son intention et de son ton.
- Utiliser le parcours d'Abdoulaye comme regard : stratégie, finance, organisation, politiques publiques, entrepreneuriat et IA appliquée.
- Ne pas ramener chaque sujet à l'IA ni chercher une mission à raconter à chaque occasion.
- Autoriser un accord développé, une appréciation précise, un rapprochement, une réserve respectueuse ou une question sincère.
- Ne pas hiérarchiser « ancré → doctrine → question » : la meilleure réponse dépend du post.
- Autoriser une opinion ou une déduction sans anecdote justificative.
- Ne jamais inventer un client, une mission, un chiffre ou un résultat personnel.
- Éviter les paraphrases, les questions déjà répondues dans le post, les compliments interchangeables et les audits non sollicités.
- Ne pas imposer une contradiction, une question finale ou la reprise d'un nom propre.
- Préserver la relecture humaine dès maintenant.

Source du parcours : `/Users/abdoulaye/Downloads/CV_Abdoulaye_CABA_2026.pdf`. Les faits de ce CV ne permettent pas d'inventer des détails de mission ou des résultats absents du document.

## 3. État du dépôt et de l'environnement

Répertoire : `/Users/abdoulaye/pestel-local/pestel-nexus-brain`.

Au début du travail, le dépôt était propre. La refonte LCR-014 était déjà présente : profil métier, expérience facultative et mode libre. Les changements LCR-015 décrits ici sont **locaux, non commités et non déployés**.

Services observés :

| Service | État observé | Rôle |
|---|---|---|
| `pestel-brain-api` | healthy | FastAPI conteneurisé |
| `pestel-postgres-local` | healthy | Posts et historique des générations |
| `n8n-app` | démarré | Collecte et orchestration |
| `n8n-postgres` | healthy | Base interne n8n |

Le conteneur FastAPI utilise `qwen3.5:9b`, transport `ollama_native`, `think=false`.

Attention : la configuration Python locale charge par défaut `gemma4:31b-cloud`. Le premier essai a explicitement forcé le modèle de production. Les évaluations suivantes doivent préciser la configuration pour éviter de comparer deux modèles sans le savoir.

Les accès Docker et réseau local ont nécessité une exécution hors sandbox. Cela a été autorisé par l'outil de revue automatique. Aucun secret n'a été ajouté au code.

## 4. Ce qui a déjà été modifié

### Politique par cible

La couche métier `app/linkedin_comments/worlds.py`, appelée par le runtime, porte les différences entre cibles. Une erreur ici affecte les sujets retenus et les critères de jugement.

- ICP1 : posture d'échange entre pairs, vouvoiement par défaut.
- ICP1 : plus d'exclusion automatique des actualités et annonces ; examiner leur contenu concret.
- Ajout d'une posture et d'une version de politique dans le registre.
- Les critères des autres mondes restent distincts : `icp1bis`, `dev`, `ai_practitioner`.

**Limite :** les consignes communes et les contrôles ont changé pour tous les mondes. Préserver leur configuration ne prouve donc pas une absence de régression éditoriale.

### Rédacteur et juge

La couche prompts, appelée par le runtime avant chaque requête LLM, est dans `app/linkedin_comments/prompts.py`.

- Version passée de `lcr-v2` à `lcr-v3-conversation`.
- Posture du monde injectée au rédacteur.
- Suppression des obligations de nom propre et de question finale.
- Précision : ne pas prétendre avoir lu un lien ou vu une image non fournie.
- Après le premier essai, simplification du juge pour distinguer une opinion d'un vécu attribué à Abdoulaye.
- Demande de raisons brèves et de corrections réalisables sans fait nouveau.
- Ajout de deux exemples fictifs de mouvements conversationnels au rédacteur.

**Point essentiel :** le premier essai a chargé les prompts AVANT cette dernière simplification. Il ne mesure pas les prompts actuellement sur disque. Les appels exacts sont conservés dans son rapport.

### Contrôles objectifs

La couche de contrôles purs, appelée après rédaction, est dans `app/linkedin_comments/controls.py`.

- Retrait des anciennes heuristiques : sujet concret obligatoire, nom propre ou chiffre obligatoire, félicitations interdites, marqueur adversatif interdit en ouverture de célébration.
- Retrait des fonctions devenues inutilisées et de leurs tests obsolètes.
- Maintien des contrôles de langue, liens, ponctuation, longueur, répétition et rattachement à l'expérience quand elle est fournie.
- Bornes actuelles : 1 à 4 phrases, 30 mots maximum par phrase.
- Correction du message de réécriture qui parlait encore de 20 mots.
- Correction de la normalisation des doublons dans le runtime : insertion et comparaison utilisent maintenant la même fonction.

**Limite :** la détection de répétition ne couvre que les tentatives d'un même run. Elle n'empêche pas les formulations ou anecdotes répétées entre plusieurs posts.

### Audit

La couche d'audit `app/linkedin_comments/audit.py` enregistre les appels du runtime. Le repository PostgreSQL les persiste ; aucune connexion DB n'a été ajoutée au cœur métier.

Ajouts :

- `editorial_context` : politique du monde, domaines métier et expérience proposée.
- `model_calls` : étape, system prompt, user payload, schéma, température, limite de tokens, réponse brute, tokens de sortie, durée et type d'erreur d'appel éventuelle.
- Le résultat HTTP expose ces champs de façon additive.
- `app/infrastructure/postgres/linkedin_comment_repository.py` les ajoute aux diagnostics JSONB existants.

**Non vérifié :** round-trip réel dans PostgreSQL, réponse de l'API déployée et taille des payloads réels dans n8n. Aucune migration n'a été appliquée.

### Évaluation reproductible

L'outil `app/linkedin_comments/dry_run.py` appelle le même runtime avec un repository sans écriture.

Ajouts :

- `--category` pour filtrer une catégorie PostgreSQL.
- `--observed-date` pour filtrer une journée UTC de collecte.
- `--output` pour conserver le rapport complet après chaque post.
- Vérification du monde demandé et d'une limite positive.

**Non vérifié :** nouveau filtrage DB par catégorie/date ; pour le premier essai, les posts ont été exportés depuis PostgreSQL puis lus en fichier.

## 5. Preuves disponibles

### Tests

| Vérification | Résultat | Ce que cela prouve |
|---|---|---|
| Suite complète avant modifications | 147 tests réussis | État initial fonctionnel selon les tests existants |
| Dernière suite `tests/linkedin_comments` | 81 tests réussis | Contrats et orchestration locale avec les changements actuels |
| Suite complète après modifications | Non exécutée | Compatibilité globale encore à vérifier |
| Derniers prompts sur modèle réel | Non évalués | Qualité éditoriale non démontrée |

Le nombre de tests a baissé dans certains fichiers parce que les règles supprimées avaient leurs propres tests. Ne pas comparer seulement les totaux : vérifier les comportements couverts.

Les nouveaux tests multi-mondes utilisent un faux LLM. Ils prouvent le passage des bonnes données et la conservation de la trace. **Ils ne prouvent pas que Qwen reconnaît réellement une fabrication ou rédige un bon commentaire.**

### Feed et premier essai

Les 17 lignes ont été collectées le 5 septembre 2026 ; les posts eux-mêmes ne datent pas nécessairement de ce jour. Deux lignes Sabrina Coulibaly Seck contiennent le même texte sur la gouvernance et son anniversaire.

Fichiers conservés dans le dépôt :

- [Feed extrait](evidence/lcr-015/feed-consultant-2026-09-05.json)
- [Rapport complet du premier essai](evidence/lcr-015/premier-essai.json)
- [Sortie lisible du premier essai](evidence/lcr-015/premier-essai.log)

Résultat : **1 draft, 15 skips, 1 erreur**. Le processus est terminé ; aucune évaluation n'est encore en cours.

Le seul draft concerne Gemini Notebook :

> Le décalage des réinitialisations à 5 heures semble effectivement utile pour éviter les interruptions en cours de session. Cela change la façon dont on planifie l'utilisation intensive de l'outil.

Appréciation éditoriale : ce brouillon reste proche d'une paraphrase et ne suffit pas à démontrer le résultat recherché. Il reprend une information du post, sans vérification externe de cette information.

Erreur constatée sur un post consacré à l'alignement pédagogique (`87ddb1f5-922b-432e-b14e-00a374eed535`) : le juge a répété ses raisons jusqu'à produire un JSON tronqué, classé `contrat_invalide:ValidationError`.

Exemples de faux rejets :

- « Votre triptyque… » interprété comme une expérience qu'Abdoulaye s'attribuerait.
- Une remarque sur les biais cognitifs traitée comme une fabrication de vécu.
- Le juge demandait parfois une expérience personnelle alors qu'aucune n'était autorisée.

Les prompts ont été corrigés après ces observations, mais leur efficacité reste à mesurer.

## 6. Travail restant, par ordre de priorité

### P0 — Vérifier les dernières consignes sur le modèle réel

- [ ] Lancer un petit lot varié avec les prompts actuellement sur disque : management, ressources limitées, formation IA, financement diaspora.
- [ ] Lire les brouillons, les motifs et les éventuelles réécritures, pas seulement le champ `outcome`.
- [ ] Vérifier que le juge autorise réellement une opinion et rejette réellement un vécu inventé.
- [ ] Vérifier qu'une appréciation précise peut être retenue sans question finale.
- [ ] Si les raisons bouclent encore, borner aussi les tableaux et les chaînes dans le schéma du juge et valider l'effet sur Qwen.
- [ ] Ne pas résoudre les faux rejets en supprimant le contrôle de véracité.

Critère : des décisions cohérentes sur des exemples positifs ET négatifs, avec raisons lisibles et sans JSON tronqué.

### P0 — Calibrer le feed complet et constituer une revue éditoriale

- [ ] Rejouer les 17 posts avec les dernières consignes, dans un nouveau rapport.
- [ ] Identifier le doublon de texte et ne pas le compter comme deux preuves indépendantes de qualité.
- [ ] Annoter chaque résultat : utilisable, retouche légère, à refaire, abstention justifiée, erreur technique.
- [ ] Pour chaque brouillon, vérifier pertinence précise, naturel, valeur pour l'auteur, véracité et absence d'offre déguisée.
- [ ] Obtenir au moins trois brouillons utilisables sur plusieurs sujets et auteurs. Ce seuil est un minimum de calibration, pas la définition exhaustive de l'objectif.
- [ ] Examiner toutes les exclusions : certaines sont raisonnables, d'autres peuvent cacher une règle trop serrée.
- [ ] Présenter les meilleurs brouillons à Abdoulaye pour recueillir sa voix réelle. Les modifications humaines doivent enrichir une future calibration plutôt que devenir automatiquement des faits biographiques.

### P1 — Consolider la traçabilité

- [ ] Tester le repository avec PostgreSQL réel : sauvegarder puis relire les diagnostics, le contexte et les appels.
- [ ] Vérifier la conservation des réponses invalides et des tentatives rejetées.
- [ ] Ajouter des tests ciblés du repository et des nouveaux champs dans la réponse FastAPI.
- [ ] Conserver les paramètres qui influencent réellement la génération : transport, think, modèle et, si disponible, digest du modèle. La trace actuelle ne contient pas tous ces paramètres.
- [ ] Clarifier que `comment_mode=ancre` signifie « expérience fournie », pas « expérience effectivement utilisée ».
- [ ] Ne pas interpréter `evidence_ids` comme une preuve de citation effective : ils sont estampillés depuis le contexte proposé.
- [ ] Décider comment versionner les révisions de prompts : les deux variantes de cette session portent encore `lcr-v3-conversation`. Le rapport exact permet de les distinguer, mais le nom de version seul ne suffit pas.
- [ ] Vérifier les motifs d'analyse : `skip_reason` est contraint dans le schéma envoyé au modèle, mais le contrat Python accepte encore une valeur absente et le runtime peut produire `analyzer_skip`.

### P1 — Assurer la compatibilité multi-cibles et la déduplication

- [ ] Tester des exemples réels pour `ai_practitioner`, puis des cas représentatifs pour `icp1bis` et `dev`.
- [ ] Vérifier que la posture ICP1 ne devient pas implicitement celle de toutes les cibles.
- [ ] Garder `category_slug` et `reader_world` distincts : une catégorie de collecte n'est pas automatiquement une politique éditoriale.
- [ ] Corriger la déduplication n8n : elle utilise actuellement post + content_hash + statut draft/skip, sans distinguer monde ni version.
- [ ] Définir une clé qui ne bloque pas un nouveau traitement pour une autre cible ou une nouvelle politique, tout en évitant les relances inutiles.
- [ ] Tester : même contenu/même politique, autre monde, nouvelle version, erreur précédente et contenu modifié.
- [ ] Préserver l'historique. Ne pas effacer les 17 skips anciens pour faire fonctionner la relance.
- [ ] Prévoir une mémoire de répétition entre posts si la calibration montre des formulations ou anecdotes recyclées. Définir son périmètre par auteur/cible et la tracer.

### P1 — Vérifier n8n → FastAPI → PostgreSQL

Workflows inspectés en lecture seule :

| Nom exact | Identifiant | État observé |
|---|---|---|
| LinkedIn Posts Comments Consultant | `aO0kX5v6cmNzRhbe` | Inactif |
| LinkedIn Posts Comments AI Practionners | `Odr7h7W64hcOhbgS` | Inactif |

Le contrat envoyé au runtime reste :

```json
{
  "linkedin_post_id": "<UUID du post enregistré>",
  "reader_world": "icp1"
}
```

Endpoint existant : `POST http://host.docker.internal:8000/v1/linkedin-comment-runs` depuis n8n.

- [ ] Vérifier que le digest continue de lire `draft`, `skip`, `error` avec les nouveaux champs additifs.
- [ ] Valider tout changement du workflow et relire ses connexions après sauvegarde.
- [ ] Tester sans déclencher Apify ni Gmail : le workflow complet collecte et envoie réellement un email.
- [ ] Reconstruire le conteneur FastAPI après validation du code.
- [ ] Vérifier sa santé, puis appeler réellement le endpoint depuis le réseau du conteneur n8n sur un post existant.
- [ ] Vérifier que le run obtenu existe en PostgreSQL avec la bonne version et la trace complète.
- [ ] Ne pas activer le planning comme conséquence implicite d'un test de compatibilité.

Points connexes observés, à évaluer sans diluer la priorité éditoriale : requêtes SQL n8n construites par expressions, cooldown de collecte désactivé, timeout et politique de retry HTTP, gestion des erreurs hors runtime. Les connexions et identifiants de credentials existants n'ont pas été modifiés.

### P2 — Rendre le code et la documentation cohérents

- [ ] Relire le diff et supprimer les commentaires historiques devenus faux : certains parlent encore du mode question, de structures imposées ou d'une seule question du juge.
- [ ] Typer explicitement les listes de traces et la fonction d'appel d'audit ; retirer les imports inutilisés.
- [ ] Réexaminer le profil métier : certaines descriptions restent centrées sur ce qui bloque ou casse, ce qui peut favoriser une posture corrective.
- [ ] Tester le filtrage `--category` / `--observed-date` et préciser la différence entre collecte, première observation et publication.
- [ ] Documenter l'usage des rapports, l'emplacement de l'audit et la procédure d'ajout d'un monde.
- [ ] Mettre à jour les tests existants pour qu'ils décrivent les règles présentes, pas seulement pour obtenir une suite verte.
- [ ] Lancer `./scripts/verify.sh` sur le dépôt complet. Le script n'exécute actuellement ni ruff ni mypy.
- [ ] Relire les risques et limites de la calibration, mettre à jour la slice, WEEKLY et BACKLOG.
- [ ] Commit sur `main` selon `AGENTS.md`, après vérification. Ne pas annoncer le chantier terminé avant la vérification de bout en bout.

## 7. Commandes utiles pour reprendre

Depuis la racine du dépôt :

```bash
./.venv/bin/pytest tests/linkedin_comments -q
./scripts/verify.sh
```

Rejouer le feed conservé avec le modèle observé en production, sans écriture DB :

```bash
OLLAMA_MODEL=qwen3.5:9b OLLAMA_THINK=false \
  ./.venv/bin/python -u -m app.linkedin_comments.dry_run \
  --world icp1 \
  --fixtures tasks/evidence/lcr-015/feed-consultant-2026-09-05.json \
  --output tasks/evidence/lcr-015/second-essai.json \
  --verbose
```

Tester ensuite le nouveau filtre DB, lorsque la connexion configurée est disponible :

```bash
OLLAMA_MODEL=qwen3.5:9b OLLAMA_THINK=false \
  ./.venv/bin/python -u -m app.linkedin_comments.dry_run \
  --world icp1 --db --category consultant \
  --observed-date 2026-09-05 --limit 30 \
  --output tasks/evidence/lcr-015/essai-filtre-db.json
```

Ces commandes ne publient rien et ne sauvegardent pas les runs en base. Ne pas écraser `premier-essai.json` : c'est la preuve de l'état précédent. Les rapports contiennent les posts et les prompts exacts ; ils sont destinés au travail local.

## 8. Documents de référence et condition de clôture

- [Spec du chantier](specs/2026-09-05-commentaires-conversation-audit.md)
- [Slice LCR-015](slices/2026-09-05-lcr-015-conversation-audit.md)
- [Suivi hebdomadaire](WEEKLY.md)
- [Backlog](BACKLOG.md)

Le chantier pourra être déclaré terminé lorsque les commentaires réels auront été relus et jugés utilisables, que les faux rejets et l'erreur constatée auront été traités, que l'audit sera relisible en PostgreSQL, que les autres mondes et le pont n8n seront vérifiés, et que le code livré correspondra à la version testée et documentée.

**Prochaine action recommandée :** exécuter les derniers prompts sur un petit lot réel et un lot de véracité avant toute modification supplémentaire importante. Le principal point d'incertitude est désormais le comportement du juge et du rédacteur sur Qwen, pas le passage des contrats Python.
