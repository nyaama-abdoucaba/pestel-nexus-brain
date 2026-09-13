# LCR-018 — La chaîne des délais, et le travail qu'on ne jette plus

**Statut** : done. Sept réglages appliqués d'un coup, sur trois endroits différents.

## Le symptôme

Digest du 06/09/2026 après le correctif LCR-017 : 4 brouillons, 8 skips,
3 `budget_execution_epuise`. Deux défauts distincts derrière ces trois erreurs.

## Défaut 1 — le budget jetait un brouillon déjà écrit

`runtime.py` vérifiait le budget entre la rédaction et le juge. Le moteur
écrivait un commentaire, constatait qu'il n'avait plus le temps de le faire
juger, et le jetait. L'un des trois contenait ceci, jamais lu par personne :

> Le temps d'exécution rapide ne doit pas masquer le temps de réflexion exigé
> par l'élève. L'enseignant devient alors un architecte de situations qui
> obligent ce travail mental.

Un budget décide si on ENTREPREND un travail, jamais s'il faut jeter un travail
déjà fait. La rédaction coûte un appel, le juge un seul de plus.

Troisième occurrence de ce motif en une semaine, après `editorial_hypothesis`
trop long et la sauvegarde qui perdait tout à la dernière ligne. Le point commun
est toujours le même : une limite pensée pour protéger, placée après la dépense.

La garde reste en place à l'entrée d'une tentative, là où elle sert.

## Défaut 2 — quatre délais qui ne s'emboîtaient pas

| Où | Avant | Après |
|---|---|---|
| client Ollama | 60 s | 60 s |
| budget moteur, `RevisionBudget` | 120 s | **150 s** |
| node n8n `Run LinkedIn Comment Runtime` | 180 s | **300 s** |

Pire cas désormais : le budget autorise une dernière tentative à 149 s, l'appel
dure au plus 60 s, total 209 s, sous les 300 s du node. Chaque niveau laisse au
précédent le temps de finir proprement.

Mesuré le 06/09/2026, machine calme : un post sain prend 11 à 17 s, trois appels.

## Défaut 3 — le retry de n8n empilait les requêtes

Le node runtime portait `retryOnFail` avec trois tentatives. Quand l'API est
lente, n8n relance pendant que le premier appel tourne toujours côté serveur :
personne ne l'annule. Explication probable des neuf requêtes Ollama en vol à
22 h 12 le 05/09/2026, alors que `OLLAMA_NUM_PARALLEL` vaut 1.

Ce retry ne servait à rien : l'appel part sur localhost, et le node porte déjà
`neverError` et `onError: continueRegularOutput`. Coupé. Les nodes Apify le
gardent, eux affrontent un vrai réseau.

## Défaut 4 — le digest comptait les succès comme des anomalies

`Build Digest` construisait son libellé en cascade : `reason_code`, puis
`diagnostics`, puis `skip_reason`, puis le code HTTP. Un brouillon réussi n'a
aucun des trois premiers. Il tombait donc sur le dernier, et la répartition
affichait `4× Appel runtime retourne HTTP 201.` au lieu de `4 brouillons`.

Le bloc dépliant `Sélection` pointait un champ supprimé avec le corpus. Remplacé
par `Domaines`, et deux lignes ajoutées à l'en-tête de chaque carte, `Domaines`
et `Régime`, qui disent pourquoi un principe a servi ou pourquoi aucun.

## Fichiers touchés

- `app/linkedin_comments/runtime.py` — la vérification de budget avant le juge
  est supprimée.
- `app/linkedin_comments/contracts.py` — budget 120 → 150 s, avec la chaîne
  documentée sur place.
- `tests/linkedin_comments/test_runtime.py` — classe `BudgetEtTravailDejaFait`,
  deux cas : un brouillon écrit est toujours jugé, et le budget arrête bien
  avant d'entreprendre une réécriture.
- n8n `aO0kX5v6cmNzRhbe`, node `Run LinkedIn Comment Runtime` — timeout 300 s,
  `retryOnFail` coupé.
- n8n `aO0kX5v6cmNzRhbe`, node `Build Digest` — libellé des brouillons, bloc
  `Domaines`, lignes `Domaines` et `Régime`.

## Vérification

    ./scripts/verify.sh          # 107 passed

Les deux nouveaux tests ont été validés à l'envers : l'ancienne vérification
remise, ils échouent tous les deux.

Le code du node `Build Digest` a été relu depuis la base PostgreSQL de n8n, pas
depuis l'API : syntaxe contrôlée par `node --check`, accents intacts, plus une
seule mention de `payload.selection`.

Réglages n8n relus en base :

    timeout        300000
    batchSize      1
    retryOnFail    false
    onError        continueRegularOutput

## Hors dépôt

`OLLAMA_KEEP_ALIVE` vaut 5 minutes par défaut. Entre deux posts d'un lot, Ollama
libère les 6 Go du modèle et les recharge ensuite. À porter à 30 minutes par
`launchctl setenv OLLAMA_KEEP_ALIVE 30m`, suivi d'un redémarrage d'Ollama.

## Le workflow praticiens IA, aligné le même jour

`Odr7h7W64hcOhbgS` avait quatre retards sur `aO0kX5v6cmNzRhbe` :

| Point | Avant | Après |
|---|---|---|
| `Config Categorie` | deux valeurs | trois, avec `prompt_version` |
| node runtime, timeout | 180 s | 300 s |
| node runtime, `retryOnFail` | trois tentatives | coupé |
| `Upsert`, déduplication | sans version | par `prompt_version` |
| `Build Digest` | ancienne version | identique au consultant |

`batchSize` valait déjà 1.

**Comment la conformité a été prouvée.** Les deux gros textes, la requête de
déduplication et le code du digest, ont été transférés par le MCP puis relus
depuis la base PostgreSQL de n8n et comparés à ceux du consultant :

    requête Upsert   4019 octets, identiques octet pour octet
    Build Digest     8555 octets, identiques octet pour octet, node --check valide

Puis une comparaison node par node des deux workflows, empreinte md5 des
paramètres, hors notes autocollantes. Un seul écart subsiste, `Config Categorie`,
et c'est précisément le node prévu pour porter la variation.

**Effet mesuré de la déduplication** sur le feed praticiens :

    posts praticiens        78
    bloqués, ancienne règle 27
    bloqués, nouvelle règle  0

**Appel réel avec `reader_world=ai_practitioner`**, HTTP 201 en 17,6 s. Le post
était en anglais. La première rédaction est sortie en français avec une
déclaration `en` : le contrôle `detected_language_mismatch` l'a attrapée sans
appeler le juge. La seconde est sortie en anglais, les contrôles ont passé, et le
juge a répondu `rewrite` parce que le commentaire reformulait la thèse du post.
Deuxième tentative atteinte, donc `juge_reecriture_epuisee`. Trois filtres dans
l'ordre du moins cher au plus cher, aucun appel gaspillé.

## Reste à faire

1. Le cooldown de 24 h reste désactivé dans `Fetch Eligible Targets`, marqué
   TEMPORAIRE, sur les deux workflows. Chaque relance rescanne les cibles chez
   Apify.
2. Rien ne mesure ce qui se passe après publication.
3. Le lot de véracité n'a pas été rejoué contre le juge de `lcr-v4`.
4. `OLLAMA_KEEP_ALIVE` reste à 5 minutes tant que la commande `launchctl` n'a pas
   été lancée.
