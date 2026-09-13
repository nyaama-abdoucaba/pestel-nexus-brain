# LCR-020 — `why_follow` arrive enfin au rédacteur

**Statut** : done, mesuré. Effet réel mais modeste, voir plus bas.

## Le constat

`why_follow` était collecté par n8n, rangé dans `linkedin_posts.raw_payload`, et
lu par personne. Zéro occurrence dans `app/`. Les 49 cibles ont toutes une note,
81 caractères en moyenne, et aucune n'a jamais influencé un commentaire.

La requête `load_post` faisait déjà la jointure vers `linkedin_targets`. Il ne
manquait qu'une colonne dans le `SELECT`.

## Ce qui a été fait

**Une frontière de confiance.** `why_follow` vient d'Abdoulaye, `text` vient du
web. Les mélanger dans la même charge utile ferait passer une source de confiance
pour une donnée non fiable, et l'inverse. La note a donc son propre bloc dans le
prompt système du rédacteur, et `_sans_note()` la retire des trois charges utiles.

**Un garde-fou.** La note dit souvent « il peut apporter du vécu sur X ». Le bloc
précise que cela veut dire qu'il connaît X, jamais qu'il a fait une chose précise
dont le modèle pourrait parler. Sans quoi la note devient une licence de
fabrication, le seul risque irréversible du dispositif.

**Trois interdits de forme** : ne pas recopier la note, ne pas la paraphraser, ne
jamais dire à la personne ce qu'on sait d'elle.

**L'analyseur et le juge ne la voient pas.** L'analyseur classe un post, le juge
relit un commentaire. Ni l'un ni l'autre n'a besoin de savoir qui publie, et le
leur donner biaiserait leur travail.

## Ce que ça change, mesuré

Trois posts, même modèle, rédacteur à température 0, avec et sans la note.

Cas 1, post sur le rachat d'OpenRouter :

    sans note : « Stripe achète OpenRouter pour gérer les coûts des appels modèles.
                  Un agent qui écrit du code fait cent appels. »
    avec note : « L'acquisition valide que les entreprises comptabilisent ce coût. »

Le sans-note est ici plus concret. Cas 2 : les deux versions sont presque
identiques. Cas 3 : la version avec note s'ancre mieux dans le post, mais frôle
le résumé.

**Verdict honnête : la note déplace le registre, elle n'améliore pas nettement le
commentaire sur ces trois cas.** La raison est dans les notes elles-mêmes. Les 49
notes actuelles décrivent le terrain de la personne, ce que le post révèle déjà.
Le format en trois parties de la nouvelle grille de sourcing, ce que la personne
fait, le terrain commun, et ce qu'Abdoulaye peut légitimement apporter, porterait
beaucoup plus de signal. La plomberie est en place, la valeur dépend maintenant du
contenu des notes.

## Fichiers touchés

- `app/linkedin_comments/contracts.py` — `LinkedInPost.why_follow`.
- `app/infrastructure/postgres/linkedin_comment_repository.py` — `t.why_follow`
  ajouté au `SELECT` de `load_post`.
- `app/linkedin_comments/prompts.py` — `_bloc_relation()`, `_sans_note()`, et les
  trois charges utiles nettoyées.
- `tests/linkedin_comments/test_conversation.py` — deux cas : la note va au
  rédacteur et nulle part ailleurs, et son absence ne laisse aucun bloc vide.

## Catégories ajoutées

    communaute     Communauté de développeurs
    pair_visible   Pair visible
    decideur_esn   Décideur ESN

Aucun changement de schéma, trois lignes dans `target_categories`.

`praticien_reference` de la grille correspond à `ai_practitioner`, qui existe
déjà avec 18 cibles. Aucune nouvelle catégorie n'a été créée pour lui.

`agence_esn_technique` existe toujours, avec LionsTech Invest et Orange Digital
Center Sénégal. Ce n'est pas la même chose que `decideur_esn` : Orange Digital
Center est un lieu de communauté, pas un acheteur. Le déplacement des deux cibles
reste à arbitrer.

## Reste à faire

1. Réécrire les `why_follow` au format en trois parties. C'est ce qui donnera sa
   valeur à cette tranche.
2. Peupler les trois nouvelles catégories.
3. Décider du monde de lecteur de chacune, et créer les workflows.
4. Arbitrer le sort de `agence_esn_technique` et de ses deux cibles.
