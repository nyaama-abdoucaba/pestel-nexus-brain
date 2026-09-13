# SPK-001 : Ollama tient-il la boucle agentique de l'API Messages ?

**Date** : 2026-09-10
**Durée décidée** : 20 minutes
**Durée réelle** : environ 15 minutes
**Statut** : répondu
**Rattaché à** : PRD CCAR, exigences F-1.1 à F-1.7

## La question

Ollama renvoie-t-il `stop_reason` avec la valeur `tool_use`, puis `end_turn`,
sur un aller-retour d'outil complet passé par `/v1/messages` ?

Cette question conditionne quatre lots du PRD. Le domaine 1 de l'examen pèse
27 % des points, et il repose entièrement sur ce champ.

## Pourquoi un spike et pas une lecture de documentation

La documentation d'Ollama annonce `stop_reason` parmi les champs de réponse
supportés. Une annonce n'est pas une preuve. Le dépôt porte déjà la trace de deux
pièges non documentés sur cette pile : le champ `think` qui casse `format` sur
certains modèles Gemma, et le tool-calling incomplet de la même famille.

## La méthode

Deux appels `curl` sur `http://localhost:11434/v1/messages`, modèle `qwen3.5:9b`.

Un outil déclaré, `donner_meteo`, qui prend une ville et rend une température.
Une question qui oblige à l'appeler : « Quel temps fait-il a Dakar ? ».

Le premier appel envoie la question seule. Le second renvoie la conversation
complète : la question, le message de l'assistant avec son appel d'outil, puis un
message portant le `tool_result`.

Aucun code applicatif n'a été touché. Les deux commandes sont dans la section
« ce qu'on jette ».

## Le résultat

| Tour | `stop_reason` | blocs dans `content` | tokens entrée | tokens sortie |
|---|---|---|---|---:|---:|
| 1 | `tool_use` | `thinking`, puis `tool_use` | 291 | 88 |
| 2 | `end_turn` | `thinking`, puis `text` | 354 | 74 |

Le bloc `tool_use` du tour 1 portait l'identifiant `call_8y4t5wlk`, le nom
`donner_meteo`, et l'entrée `{"ville": "Dakar"}`.

Le bloc `text` du tour 2 reprenait la température fournie, en français, avec la
mise en forme du modèle.

## La réponse

Oui. La boucle agentique complète fonctionne sur cette machine, avec ce modèle.

Le champ `stop_reason` porte bien les deux valeurs attendues, dans le bon ordre.
Une boucle qui continue tant que `stop_reason` vaut `tool_use` et s'arrête sur
`end_turn` peut donc s'écrire et se tester en local, sans appel payant.

## Ce que l'essai a appris en plus

Quatre constats, aucun ne faisait partie de la question.

### 1. L'identifiant d'appel d'outil ne suit pas le format d'Anthropic

Ollama a produit `call_8y4t5wlk`. L'API Claude produit des identifiants préfixés
par `toolu_`.

Règle qui en découle : un identifiant d'appel d'outil se renvoie tel quel dans le
champ `tool_use_id`. Il ne se valide pas, il ne se reconstruit pas.

### 2. Le bloc `tool_use` n'est pas le premier bloc de `content`

Le modèle a placé un bloc `thinking` devant, aux deux tours. Un code qui lirait
`content[0]` en supposant y trouver l'appel d'outil échouerait ici.

Le code du dépôt gère déjà ce cas correctement. Dans
`app/linkedin_comments/ollama_anthropic.py`, la recherche se fait par type et par
nom, jamais par rang :

    tool_call = next(
        (
            block for block in message.content
            if getattr(block, "type", None) == "tool_use"
            and getattr(block, "name", None) == _TOOL_NAME
        ),
        None,
    )

### 3. Ollama accepte un message assistant amputé de son bloc `thinking`

Le second appel a volontairement renvoyé le bloc `tool_use` seul, sans le bloc
`thinking` qui le précédait. Ollama a accepté la requête et répondu correctement.

L'API Claude refuse ce raccourci. Sa documentation pose deux règles. Les blocs
`thinking` doivent revenir avec le résultat d'outil. Le message assistant doit
être renvoyé exactement tel qu'il a été reçu, sans reconstruction ni filtrage,
sous peine d'une erreur HTTP 400.

La raison est visible dans le format. Chez Claude, un bloc `thinking` porte un
champ `signature` qui scelle son contenu. Le bloc `thinking` d'Ollama n'en a pas.

**Ce constat va dans le sens inverse du risque attendu.** On redoute d'habitude
qu'un code écrit pour un grand modèle casse sur un modèle local moins capable.
Ici, le local est plus permissif que le distant. Il laisse passer une requête que
Claude refuserait.

Un environnement permissif est plus dangereux qu'un environnement strict. Le
strict signale la faute tout de suite. Le permissif laisse construire dessus
pendant des semaines, et la faute apparaît le jour de la bascule, sur du code que
les tests déclarent bon.

Conséquence pour le PRD : la voie agentique de `app/agents/` doit renvoyer le
tableau `content` de l'assistant en entier, sans filtrer aucun bloc. Cette
discipline ne sert à rien sur Ollama. Elle sert le jour où la même boucle pointe
vers l'API Claude.

### 4. Le contexte grossit de 63 tokens pour un aller-retour trivial

Les tokens d'entrée sont passés de 291 à 354. La question faisait sept mots, et
le résultat d'outil neuf.

Les 291 tokens du premier appel sont déjà presque tous consommés par la
déclaration de l'outil, pas par la question.

Ce compteur donne une base chiffrée à l'exigence F-5.1, qui impose d'élaguer les
sorties d'outil avant leur accumulation. Sur quinze tours, l'historique pèse plus
que la demande.

## Ce que ça décide dans le PRD

| Élément | Effet |
|---|---|
| Exigences F-1.1 à F-1.7 | débloquées, la mécanique est prouvée en local |
| Lot L4, boucle agentique et coordinateur | peut démarrer sans réserve technique |
| Exigence F-5.1, élagage du contexte | confirmée par une mesure, plus seulement par principe |
| Section 7.1 du PRD | à compléter avec les quatre constats ci-dessus |

Aucun lot n'est bloqué par ce spike. La question qui gardait le plus de risque
est levée.

## Les limites de cet essai

Un seul modèle testé, `qwen3.5:9b`. Un seul outil déclaré. Un seul aller-retour.

L'essai ne dit rien de trois points qui comptent pour la suite. Le comportement
avec plusieurs outils déclarés en même temps, que l'examen désigne comme une
source de mauvais aiguillage. Le comportement sur cinq tours ou plus. La qualité
du choix d'outil quand deux descriptions se ressemblent, qui fait l'objet de
l'exigence F-2.1.

Ces trois points se mesureront dans le lot L3, sur le serveur `pestel-mcp`.

## Ce qu'on jette, ce qu'on garde

**On jette** les deux commandes `curl`. Elles ont répondu à leur question, elles
n'ont pas vocation à survivre.

**On garde** le scénario du second appel, sous forme de test avec un faux client.
Un test qui vérifie que la boucle s'arrête sur `end_turn` et continue sur
`tool_use` n'a besoin ni d'Ollama ni du réseau. Il tient en quelques lignes, sur
le modèle des tests existants qui exercent `LinkedInCommentRuntime` sans base ni
modèle.

Le premier appel ne mérite pas de test permanent. Il vérifie le comportement
d'Ollama, pas celui du code du dépôt. Sa place est ici, dans ce spike daté.
