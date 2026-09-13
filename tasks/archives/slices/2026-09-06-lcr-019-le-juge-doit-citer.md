# LCR-019 — Le juge doit citer avant de juger

**Statut** : done, mesuré. `PROMPT_VERSION = lcr-v5-juge-cite`.

## Le symptôme

Sous un post qui disait « Privilégiez des dispositifs qui exigent de l'analytique
humaine, du jugement critique », le moteur a produit ceci, et le juge l'a
approuvé :

> Une consigne qui demande une analyse critique reste valide même si l'outil
> change. L'évaluation mesure la capacité à penser, pas seulement à exécuter un
> algorithme.

Le tell était dans `editorial_hypothesis`, écrit par le modèle : « **Je
confirme** que la validité d'une tâche dépend de ce qu'elle exige de l'humain. »
Confirmer la thèse de l'auteur, c'est par construction ne rien ajouter.

Et le juge, dont `_ANTI_PLATITUDE` disait déjà « une reformulation de la thèse de
l'auteur, même élégante, n'apporte rien : rewrite », a répondu « ce qui n'est pas
explicitement développé dans le texte original ». C'est faux. Il n'était pas allé
regarder.

## Ce qui a été changé

**Au rédacteur.** `_INTERDITS` interdit désormais de confirmer ou reformuler la
thèse de l'auteur. `editorial_hypothesis` doit nommer ce que le commentaire
ajoute et que le post ne dit pas.

**Au juge.** Un champ `passage_le_plus_proche` déclaré EN PREMIER dans le schéma.
Ollama contraint la sortie par une grammaire dérivée du schéma et remplit les
champs dans l'ordre déclaré : le juge produit donc sa citation avant son verdict,
jamais après pour l'habiller.

## Les trois essais, et ce qu'ils ont appris

Sept brouillons figés, juge à température 0, donc reproductible. Le même
brouillon passé à l'ancien juge et au nouveau.

| Version du juge | rewrite déclenchés sur 7 |
|---|---|
| avant, question abstraite | 0 |
| v1, citation obligatoire | **3** |
| v2, `apport_du_commentaire` en texte libre, avant le verdict | 0 |
| v3, même champ fermé sur cinq étiquettes | 0 |

La v2 et la v3 ont rendu le juge PLUS indulgent. Demander à un modèle de nommer
ce qu'un commentaire apporte est une question suggestive : elle présuppose
l'apport, et il en trouve un. En texte libre il écrivait « il valide cette idée
**et** précise que... », s'échappant par la conjonction. En liste fermée il
choisissait `precision_absente` cinq fois sur sept et `reformulation` jamais.

Retour à la v1. Ce qui travaille, c'est la citation, pas la question qui la suit.

Détail qui compte aussi : en v1, `reasons` restait déclaré APRÈS `decision`. Le
juge citait, décidait, puis justifiait. Sur trois cas il a écrit « le commentaire
valide directement l'idée mentionnée dans le post » et a approuvé quand même. Le
raisonnement arrivait trop tard pour peser. Ce défaut subsiste : il est la limite
mesurée de ce modèle sur cette tâche, pas un réglage oublié.

## La chaîne complète, mêmes 17 posts

| Issue | avant | après |
|---|---|---|
| draft | 6 | 4 |
| `aucune_idee_autonome` | 9 | 9 |
| `juge_reecriture_epuisee` | 1 | 3 |
| `juge_reject` | 1 | 1 |

Le mécanisme fonctionne : **11 appels du juge, 11 citations non vides, 0 « aucune »**.

**La prise nette**, sur un post consacré au dispositif AYENA :

    avant  ✔ « Réunir les institutions au même endroit fait gagner du temps. »
    le post  « Réunir ces institutions au même endroit simplifie les rendez-vous. »
    après  ✘ le juge cite cette phrase et refuse

C'est exactement le défaut signalé, attrapé sur pièce.

**Le coût.** Deux brouillons perdus sur six. L'un d'eux, sur le discernement en
RH, était défendable. Un faux positif sur six cas.

## Limite de cette mesure

Le rédacteur tourne à température 0,5. Un seul passage de chaque côté, donc les
brouillons diffèrent d'un tour à l'autre indépendamment du changement. Le duel du
juge, lui, est propre : température 0 et brouillons figés.

## Fichiers touchés

- `app/linkedin_comments/prompts.py` — schéma du juge, `_ANTI_PLATITUDE`,
  `_INTERDITS`, consigne `editorial_hypothesis`, `PROMPT_VERSION`.
- `app/linkedin_comments/contracts.py` — `JudgeResult.passage_le_plus_proche`.
- n8n, les deux `Config Categorie` — `prompt_version = lcr-v5-juge-cite`.

## Preuves

- `tasks/evidence/lcr-019/avant.json`, `apres.json` — les 17 posts, deux fois.
- `tasks/evidence/lcr-019/duel-juge.json`, `-v2`, `-v3` — les trois essais du juge.

## Reste à faire

1. Rejouer le lot de véracité contre ce juge : `_ANTI_FABRICATION` n'a pas changé,
   mais le schéma si.
2. Décider si perdre deux brouillons sur six est un prix acceptable. Point métier.
3. Refaire la mesure avec plus d'un passage par côté, pour sortir du bruit.
