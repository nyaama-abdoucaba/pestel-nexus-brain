# Spec — les domaines portent les principes, le corpus disparaît

Date : 2026-09-05. Statut : implémenté, mesuré sur le feed consultant.

## Le constat

Le moteur partait du corpus d'ancrages. Il cherchait un vécu à placer, puis une
façon de l'insérer. Deux mesures ont clos le débat.

Sur le feed consultant, **le sélecteur a refusé les ancrages 27 fois sur 27**.
Aucun commentaire ancré n'a jamais été produit, dans aucun monde.

Sur les 50 tags de situation, **35 n'atteignaient qu'un seul ancrage**. Tout post
parlant de gouvernance recevait la même histoire. Quinze faits datés ne couvrent
pas la diversité d'un fil d'actualité, et les recycler ferait dire la même chose
à tous les commentaires.

Abdoulaye a tranché : énumérer une vie professionnelle dans une application est
un autre travail que celui de commenter.

## La chaîne retenue

```
le post touche-t-il un de mes domaines ?
    oui  -> les principes de ces domaines sont proposés au rédacteur
            il en retient un, ou aucun
    non  -> il répond en conversation
```

Les douze principes quittent `corpus.py` pour `profil.py`, répartis dans les six
domaines du CV. L'analyseur ne produit plus 50 tags mais répond à une question
fermée sur six valeurs, ce qu'un modèle de neuf milliards de paramètres classe
bien plus sûrement.

`corpus.py`, `corpus.json` et le sélecteur sont supprimés. Le texte des ancrages
reste dans l'historique git.

## Aucune règle Python sur le fond ni le style

Décision d'Abdoulaye. `controls.py` passe de 250 à 130 lignes. Sont retirés : le
nombre de phrases, la longueur des phrases, la ponctuation, le sujet concret, la
présence d'un terme du post, l'interdiction de féliciter.

Motif : ces règles jugent mal. Le compte de phrases se trompait sur « Gemini 3.8 ».
L'interdiction de trois mots creux a produit quatre synonymes. La présence
obligatoire d'un nom propre forçait des tournures artificielles.

Restent quatre règles qui constatent un fait sans interpréter une intention :
langue déclarée, langue écrite, absence de lien, absence de doublon.

## Le prompt porte la voix

Le rédacteur reçoit les règles d'écriture du `CLAUDE.md` d'Abdoulaye, qui
existaient par écrit et qu'il ne connaissait pas. Il produisait « crucial » et
« essentiel » cinq fois sur quatorze brouillons, alors que les deux mots figurent
dans sa liste de mots creux interdits.

Il reçoit aussi cinq exemples validés par lui, écrits sur de vrais posts du feed.
Une voix ne se décrit pas, elle se montre.

## Deux régressions introduites puis corrigées le même jour

**L'énumération est une instruction.** Les valeurs `anti_corpus:*` étaient restées
dans le schéma du skip alors que `icp1` ne rejette plus l'actualité. Le modèle les
a employées sept fois sur dix-sept. Le vocabulaire du skip suit maintenant le
monde.

**La frontière du vécu.** Une première rédaction interdisait « toute observation
de terrain ». Le juge a rejeté les exemples validés par Abdoulaye, traitant « c'est
la question qu'on saute le plus souvent » comme un vécu, et a demandé d'ajouter
une expérience réelle. La frontière n'est pas entre le général et le particulier,
elle est entre ce qu'on affirme avoir fait et ce qu'on pense.

## Résultats mesurés, feed consultant, 17 posts

| | avant | après |
|---|---|---|
| brouillons | 1 | 8 |
| « semble » | 8/14 | 0/8 |
| mots creux interdits | 7/14 | 0/8 |
| ouverture répétée | 3 fois | aucune |
| commentaires finissant par une question | 3/14 | 2/8 |

Les huit skips sont des vœux, un anniversaire, des promotions d'événement et un
post politique. Écarter est la bonne décision sur tous.

## Ce qui reste

Un anglicisme de la liste interdite est passé dans un brouillon sur huit.

Le lot de véracité n'a pas été rejoué depuis la réécriture du juge : 6 fabrications
sur 6 étaient attrapées avec la version précédente.

Rien ne mesure ce qui se passe après publication.
