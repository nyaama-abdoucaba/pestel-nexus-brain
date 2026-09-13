# Le process de travail, du PRD au ticket

Ce document décrit la chaîne complète de production de `pestel-nexus-brain`.
Il répond à une seule question : quel document écrire, quand, et avec quoi dedans.

Il s'adresse à Abdoulaye et aux agents qui travaillent sur ce dépôt. Il remplace
les usages implicites installés depuis mai 2026.

## 1. La carte

```text
 besoin
   │
   ▼
┌─────────┐   pourquoi et quoi, en langage métier
│   PRD   │   docs/prd/                       décide : Abdoulaye
└────┬────┘
     │  découpé en
     ▼
┌─────────┐   un chantier qui dure plusieurs semaines
│  EPIC   │   tasks/epics/                    décide : Abdoulaye
└────┬────┘
     │  chaque exigence devient
     ▼
┌─────────┐   comment, en langage technique
│  SPEC   │   tasks/specs/                    décide : l'agent
└────┬────┘
     │  si une inconnue bloque          si un choix est irréversible
     ├──────────────► ┌───────┐         ├──────────────► ┌─────┐
     │                │ SPIKE │         │                │ ADR │
     │                │tasks/ │         │                │docs/│
     │                │spikes/│         │                │déci-│
     │                └───┬───┘         │                │sions│
     │  ◄─────────────────┘             │  ◄─────────────└─────┘
     ▼
┌─────────┐   une tranche livrable, testée, mesurée
│  SLICE  │   tasks/slices/                   exécute : l'agent
└────┬────┘
     │  implémentée sur
     ▼
┌─────────┐   branche, revue, fusion
│   PR    │   GitHub                          valide : Abdoulaye
└────┬────┘
     │
     ▼
 WEEKLY.md et BACKLOG.md mis à jour
```

Deux mouvements traversent cette carte. Le PRD descend vers le code. Les preuves
remontent vers le PRD, sous forme de mesures écrites dans `tasks/evidence/`.

## 2. Le vocabulaire

Le métier du logiciel a ses noms, ce dépôt a les siens. Voici la correspondance,
pour lire une documentation extérieure sans se perdre.

| Nom courant dans le métier | Nom dans ce dépôt | Emplacement |
|---|---|---|
| PRD, Product Requirements Document | PRD | `docs/prd/` |
| Epic | epic | `tasks/epics/` |
| Design doc, RFC, spec technique | spec | `tasks/specs/` |
| ADR, Architecture Decision Record | décision | `docs/decisions/` |
| Spike, proof of concept | spike | `tasks/spikes/` |
| Ticket, issue, user story | slice | `tasks/slices/` |
| Test report | preuves | `tasks/evidence/` |
| Sprint board | suivi hebdomadaire | `tasks/WEEKLY.md` |
| Product backlog | backlog | `tasks/BACKLOG.md` |

Le mot slice remplace ticket dans tout ce dépôt. Une slice n'est pas une tâche,
c'est une tranche verticale : elle traverse les couches et laisse le système
utilisable à la fin.

## 3. Le PRD

### Ce que c'est

Le PRD porte le pourquoi et le quoi d'un chantier, en langage métier. Il ne dit
jamais comment. Un lecteur qui ne connaît ni Python ni Ollama doit le comprendre
en entier.

Son objectif tient en une phrase : figer ce qu'on veut obtenir, avant de discuter
des moyens.

### Ce qu'il contient

| Section | Rôle | Piège à éviter |
|---|---|---|
| Contrôle du document | version, date, statut, auteur | oublier de versionner, le PRD devient intraçable |
| Résumé exécutif | l'idée directrice en trois paragraphes | résumer le plan au lieu d'annoncer le résultat |
| Contexte et problème | l'état actuel, l'écart constaté | décrire une solution déguisée en problème |
| Objectifs et hors périmètre | ce qui entre, ce qui sort, avec la raison | laisser le hors périmètre implicite |
| Indicateurs de succès | comment on saura que c'est réussi | poser des indicateurs qu'on ne mesurera jamais |
| Utilisateurs et cas d'usage | qui s'en sert et pour quoi | inventer des utilisateurs qui n'existent pas |
| Faisabilité | ce qui est possible, ce qui ne l'est pas, vérifié | affirmer sans vérifier |
| Exigences fonctionnelles | une par ligne, codée, avec critère d'acceptation | écrire une exigence sans critère vérifiable |
| Plan de livraison | les lots et leur ordre | ordonner par facilité au lieu du risque |
| Risques | effet, probabilité, parade | lister des risques sans parade |
| Décisions | ce qui est arbitré, ce qui reste ouvert | laisser un « à valider » sans échéance |
| Traçabilité | chaque exigence pointe vers son artefact | rompre le lien entre exigence et code |

### Ce qu'il ne contient pas

Aucun nom de bibliothèque. Aucun schéma de table. Aucun extrait de code, sauf
quand une commande porte une décision métier. Ces éléments vivent dans la spec.

### Quand il est fini

Le PRD est fini quand chaque exigence porte un critère d'acceptation qu'on peut
vérifier sans discussion, et quand aucune décision métier ne reste en suspens
sans échéance.

### Qui décide

Abdoulaye. Les seuils, les catégories, les règles de tri et les périmètres ne se
tranchent jamais dans le code.

### Sa durée de vie

Le PRD survit à ses slices. Il se lit deux ans plus tard pour comprendre pourquoi
le produit est ainsi. Il vit donc dans `docs/`, pas dans `tasks/`.

Après validation, il devient une référence figée. Toute évolution passe par une
montée de version et une ligne dans le contrôle du document. Le PRD ne se réécrit
pas en silence.

## 4. L'epic

### Ce que c'est

Un epic regroupe les slices d'un même chantier. Il existe pour répondre à une
question de suivi : où en est ce chantier, et que reste-t-il.

### Ce qu'il contient

Le nom du chantier, son code, le PRD dont il descend, la liste de ses slices avec
leur statut, et la définition de sa fin. Rien d'autre.

### Quand il est fini

Quand toutes ses slices sont fusionnées et que ses indicateurs sont mesurés.

## 5. La spec technique

### Ce que c'est

La spec dit comment. Elle traduit une ou plusieurs exigences du PRD en décisions
techniques. Elle se relit avant l'implémentation, jamais après.

Son objectif : rendre l'implémentation ennuyeuse. Quand la spec est bonne, écrire
le code ne pose plus de question.

### Ce qu'elle contient

- Le chemin actif visé, sous forme de trajet de bout en bout.
- Les fichiers touchés, avec la couche que chacun porte.
- Les contrats de données : schémas, champs, types, valeurs autorisées.
- Les migrations de base, avec leur rollback.
- Les cas d'erreur, et le comportement attendu pour chacun.
- Les critères d'acceptation, repris du PRD et rendus testables.
- Ce qui reste hors périmètre de cette spec.

### Ce qu'elle ne contient pas

Aucune justification métier. Si la spec doit défendre un seuil ou une règle de
tri, c'est que la décision n'a pas été prise dans le PRD. Il faut remonter.

### Quand elle est fini

Quand un agent peut implémenter sans poser de question, et quand chaque critère
d'acceptation se traduit en test.

### Qui décide

L'agent. Le choix d'une bibliothèque, la structure d'un dossier, le nom d'une
variable ne remontent pas à Abdoulaye.

## 6. L'ADR, ou décision d'architecture

### Ce que c'est

Un ADR enregistre un choix technique difficile à défaire. Il tient sur une page.
Il se lit dans deux ans par quelqu'un qui demande pourquoi le code est ainsi.

### Quand en écrire un

Trois signaux, un seul suffit. Le choix engage plusieurs mois. Revenir en arrière
coûterait plus d'une journée. Une personne raisonnable aurait choisi autrement.

Exemples pris dans ce dépôt : la séparation analyseur, rédacteur et juge en trois
appels distincts. Le passage par `Protocol` plutôt que par des classes concrètes
dans `runtime.py`. Le choix du champ `format` d'Ollama plutôt que de `tool_use`.

### Ce qu'il contient

| Section | Contenu |
|---|---|
| Titre | une phrase à l'affirmatif, qui énonce la décision |
| Date et statut | proposé, accepté, remplacé par un autre ADR |
| Contexte | la situation qui force un choix, sans la solution |
| Options envisagées | deux ou trois, avec leur coût |
| Décision | ce qui est retenu, et pourquoi |
| Conséquences acceptées | ce que ce choix rend difficile, assumé par écrit |

La dernière section porte toute la valeur. Un ADR qui ne liste que des avantages
n'enregistre pas une décision, il enregistre une satisfaction.

### Ce qu'il ne devient jamais

Un ADR ne se modifie pas. Quand la décision change, un nouvel ADR remplace
l'ancien, et l'ancien passe en statut remplacé. L'historique des choix compte
autant que le choix courant.

## 7. Le spike

### Ce que c'est

Un spike est une exploration bornée dans le temps, qui répond à une question dont
dépend l'architecture. Son code est jetable par construction.

Sa règle fondatrice : on ne planifie pas un travail dont l'inconnue technique
n'est pas levée.

### Ce qu'il contient

La question posée, en une phrase fermée. La durée maximale, décidée avant de
commencer. La méthode. Le résultat obtenu, avec les commandes et les sorties
réelles. La réponse à la question. Ce qu'on jette et ce qu'on garde.

### Quand il est fini

Quand la question a une réponse, ou quand la durée est écoulée. Un spike qui
dépasse son temps est un spike raté, et un spike raté est une information utile :
il dit que la question est plus profonde qu'on ne le croyait.

### Exemple applicable aujourd'hui

Le PRD CCAR affirme qu'Ollama renvoie `stop_reason` sur `/v1/messages`. Cette
affirmation vient de la documentation, pas de la machine. Un spike de vingt
minutes la vérifie, et son résultat décide si le lot 4 tient debout.

## 8. La slice, le ticket de ce dépôt

### Ce que c'est

Une slice est l'unité de travail livrable. Elle traverse les couches et laisse le
système utilisable à la fin. Elle porte un code et une date.

### La règle d'entrée

Une slice ne commence pas tant que ces quatre points ne sont pas vrais.

1. Une spec la couvre.
2. Ses critères d'acceptation sont écrits et testables.
3. Aucune inconnue technique ne bloque son chemin, sinon un spike passe d'abord.
4. Les fichiers touchés sont identifiés.

### La règle de sortie

Une slice n'est pas finie tant que ces six points ne sont pas vrais.

1. `./scripts/verify.sh` passe au vert.
2. Un test anti-régression couvre le comportement corrigé ou ajouté.
3. Les preuves sont écrites dans `tasks/evidence/` quand le changement se mesure.
4. La PR est fusionnée.
5. `tasks/WEEKLY.md` et `tasks/BACKLOG.md` sont à jour.
6. Un ADR existe si un choix irréversible a été pris en route.

### Ce qu'elle contient

Le format en vigueur dans ce dépôt, éprouvé sur les slices LCR, tient en sept
parties.

| Partie | Rôle |
|---|---|
| Le symptôme | ce qui n'allait pas, avec un cas réel |
| Ce qui a été changé | le diff raconté, fichier par fichier |
| La mesure | avant et après, sur le même échantillon |
| La prise nette | un exemple unique où le changement se voit |
| Le coût | ce que le changement a dégradé, assumé |
| Les limites de la mesure | ce que l'essai ne prouve pas |
| Le reste à faire | numéroté, avec les points métier signalés |

La partie coût et la partie limites sont obligatoires. Une slice qui ne montre
que des gains cache son prix, et ce prix se paiera plus tard sans être compris.

## 9. La PR

### La règle Git en vigueur

Une branche par slice. Une PR par branche. Aucun commit direct sur `main`.

Cette règle remplace celle en vigueur jusqu'au 2026-09-10, qui interdisait les
branches. Le changement vient du PRD CCAR, section 9.6.

### Le nom de la branche

`slice/<code-de-la-slice>`, en minuscules. Exemple : `slice/lcr-021`.

### Ce que contient la description de PR

Le code de la slice, le lien vers son fichier, et la liste des critères
d'acceptation avec une case cochée par critère vérifié. Rien de plus. La matière
vit dans la slice, pas dans la PR.

### La revue

Deux voies tournent sur chaque PR, décrites dans le PRD CCAR, section 9.6.
La revue automatique publie ses constats en commentaires. Abdoulaye valide la
fusion.

### La fusion

Après fusion, la branche est supprimée. La slice passe en statut done dans
`tasks/WEEKLY.md`.

## 10. Les cas particuliers

### Le hotfix

Production cassée, endpoint en erreur, données perdues. Le correctif passe en
priorité, avant toute documentation.

Le process ne disparaît pas pour autant. La spec et la slice se créent dans la
même session, avant de passer à autre chose. La slice porte la mention hotfix
rétroactif. L'urgence justifie l'ordre, jamais l'oubli.

### Le changement de PRD après validation

Une exigence évolue, un périmètre s'ouvre, une décision tombe. Le PRD monte d'une
version, et le contrôle du document enregistre la date et la nature du changement.
Les slices déjà fusionnées ne se réécrivent pas.

### La découverte en cours de slice

L'implémentation révèle un problème que la spec n'avait pas vu. Deux cas.

Si le problème tient dans la slice, il s'y traite, et la slice le mentionne.
Si le problème dépasse la slice, une nouvelle slice naît dans `BACKLOG.md`, et la
slice en cours se termine sur son périmètre initial. Élargir une slice en cours de
route est la façon la plus courante de ne jamais la finir.

## 11. L'arborescence cible

```text
docs/
  PROCESS.md              ce document
  ARCHITECTURE.md         comment le système est fait, pour un lecteur qui apprend
  DOMAIN_CONTEXT.md       le métier, les mondes, les cibles
  prd/                    les PRD, un par chantier majeur
  decisions/              les ADR, un par choix irréversible
  architecture/           les vues détaillées d'un sous-système
  runbooks/               les procédures d'exploitation
  standards/              les conventions transverses

tasks/
  WEEKLY.md               le tableau de bord de la semaine
  BACKLOG.md              ce qui attend
  epics/                  les chantiers
  specs/                  les specs techniques
  slices/                 les tranches livrées
  spikes/                 les explorations bornées
  evidence/               les mesures, en JSON ou en markdown
  archives/               ce qui est clos et n'est plus consulté
```

Deux dossiers manquent aujourd'hui et sont à créer : `docs/prd/` et
`tasks/spikes/`. Le dossier `docs/decisions/` existe mais reste vide.

## 12. Un exemple déroulé

La slice LCR-019, livrée le 2026-09-06, montre la chaîne en entier.

**Le besoin.** Le juge approuvait des commentaires qui reformulaient la thèse de
l'auteur. Un commentaire qui confirme n'apporte rien.

**Ce qui a manqué.** Aucun PRD ne portait ce besoin, et aucune spec ne l'a
précédé. Le travail est parti du symptôme directement vers le code.

**Ce qui a bien marché.** La slice porte tout ce qu'il faut : le symptôme avec un
cas réel, trois essais comparés, la mesure sur dix-sept posts, la prise nette sur
le post AYENA, le coût de deux brouillons perdus sur six, les limites de la
mesure, et un reste à faire numéroté.

**Ce qui aurait changé avec le process complet.** Le troisième point du reste à
faire dit : décider si perdre deux brouillons sur six est acceptable, point
métier. Cette question aurait dû être tranchée avant l'implémentation, pas
après. Un PRD l'aurait posée en question fermée.

**La leçon.** La qualité de restitution de ce dépôt est déjà professionnelle. Ce
qui manque se situe en amont : la décision métier arrive après le code, alors
qu'elle devrait le précéder.

## 13. Le résumé en une page

| Étape | Question à laquelle elle répond | Qui décide | Où |
|---|---|---|---|
| PRD | pourquoi et quoi | Abdoulaye | `docs/prd/` |
| Epic | où en est ce chantier | Abdoulaye | `tasks/epics/` |
| Spec | comment | l'agent | `tasks/specs/` |
| ADR | pourquoi ce choix, et ce qu'il coûte | l'agent, validé par Abdoulaye | `docs/decisions/` |
| Spike | est-ce que ça marche vraiment | l'agent | `tasks/spikes/` |
| Slice | qu'est-ce qui a changé, et à quel prix | l'agent | `tasks/slices/` |
| PR | est-ce que ça peut entrer dans `main` | Abdoulaye | GitHub |
