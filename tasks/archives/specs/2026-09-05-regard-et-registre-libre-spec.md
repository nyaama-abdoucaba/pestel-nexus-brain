# Spec — le regard remplace l'ancrage obligatoire

Date : 2026-09-05. Statut : implémenté, à mesurer.

## Le constat qui déclenche

Premier lot réel sur le monde `icp1`, 12 consultants : **17 posts, zéro
brouillon**. Huit posts jugés commentables sont sortis en
`selecteur_aucun_ancrage`.

L'arithmétique du corpus explique pourquoi. Sur les 50 tags de situation,
35 n'atteignaient qu'un seul ancrage. Tout post parlant de gouvernance recevait
la même histoire de moteur produisant du texte générique, tout post parlant de
transformation la même application web bloquée par l'informatique. Quinze
ancrages ne peuvent pas couvrir la diversité d'un feed, et les recycler ferait
dire la même chose à tous les commentaires.

## Ce qui est décidé

**Un ancrage n'est plus une condition.** Le réglage `ancrage_requis` est retiré
du registre des mondes. Un réglage qui ne varie plus est un réglage mort. Le
`comment_mode` du résultat vaut `ancre` quand une expérience vérifiée a été
injectée, `libre` sinon.

**Un troisième objet éditorial : le regard.** `profil.py` déclare six domaines
tirés du CV, formulés en « ce qu'il voit » et non en « ce qu'il sait faire ». Un
domaine n'affirme rien, donc il n'a rien à prouver. C'est la différence avec les
« leçons de domaine » envisagées le même jour puis écartées : une leçon
généralise à partir d'un cas et devient une affirmation à défendre.

**Plus de structure imposée par type de post.** Les cinq structures commandaient
toutes un mouvement correctif. Devant un post célébrant une formation réussie
pour cinquante TPE, le cadre interdisait de féliciter et exigeait de pointer un
coût caché. Elles sont remplacées par une liste de mouvements sans préférence.

**Plus de hiérarchie de registres.** L'ordre « ancré, puis doctrine, puis
question » classait dernier le seul registre qui avait produit des commentaires
jugés bons sur le feed des praticiens IA.

**Le garde-fou change de nature.** Il passe du code au juge, en première
question, éliminatoire. Une regex sur « j'ai vu » rejetterait « j'ai accompagné
des startups », qui est l'identité d'Abdoulaye, et laisserait passer « on
constate souvent que », qui est une invention sans première personne. Tous les
contrôles de `controls.py` portent sur la forme ; celui-ci porte sur le fond.

## Le risque assumé

Fabriquer un vécu était impossible par construction. C'est désormais
`qwen3.5:9b` qui en décide. La fiche 07 du coffre appelle ce risque le seul
irréversible du dispositif.

Deux atténuations en place : le juge reste aveugle au cadrage du rédacteur, et il
reçoit le champ `experience_autorisee`, ou `null` quand aucun vécu n'est permis.

**Ce qui manque : la mesure.** Tant qu'un jeu de brouillons fabriqués n'a pas été
soumis au juge, « le juge s'en occupe » est une intention, pas une garantie.
C'est le principe p2 appliqué au dispositif lui-même.

## Ce qui n'est pas traité

Rien ne mesure ce qui se passe après publication. `linkedin_comment_runs`
enregistre ce qui a été produit, jamais les réponses obtenues, les échanges
poursuivis ou les connexions acceptées. Sans ça, aucun registre ne peut être
déclaré meilleur qu'un autre pour l'objectif commercial.
