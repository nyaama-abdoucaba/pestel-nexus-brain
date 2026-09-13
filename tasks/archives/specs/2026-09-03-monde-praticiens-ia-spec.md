# Spec — un monde de lecteur sans intention commerciale

Date : 2026-09-03. Statut : implémenté, en attente d'arbitrage sur les sorties.

## Le problème

Le moteur a été écrit pour un seul rôle commercial : vendre. Chaque commentaire
doit prouver une compétence vécue par un ancrage du corpus, et sans ancrage le
moteur se tait. C'est la bonne règle devant un acheteur.

La base contient une autre population, déjà classée sous la catégorie
`ai_practitioner` : dix-huit praticiens IA suivis par veille, soixante-quinze
posts archivés. Abdoulaye ne leur vend rien. Ils sont plus qualifiés que lui sur
leur terrain. L'objectif est d'être vu contribuer, pas de prouver.

Deux règles du moteur rendaient ce monde inutilisable.

L'anti-corpus « actualité IA, annonce produit, sortie de framework » de la fiche
07 était écrit en dur dans le prompt de l'analyseur. Chez ce public, l'actualité
IA est le métier : la règle rejetait presque tout le feed.

L'ancrage obligatoire produisait un silence sur chaque post. Vérifié sur trente
posts réels : le sélecteur a répondu « aucun » à chaque fois. Le corpus, bâti sur
SEN-RE et la commande publique sénégalaise, ne prouve rien devant un post sur
WebMCP ou sur NVIDIA.

## Ce qui est décidé

Un registre de mondes déclarés, `worlds.py`, porte les deux rôles commerciaux de
la fiche 04 et ce qui change avec eux.

| Rôle | Mondes | Ancrage | Anti-actualité | Question du juge |
|---|---|---|---|---|
| vendre | `icp1`, `icp1bis`, `dev` | obligatoire | active | apporte-t-il quelque chose au lecteur ? |
| se faire voir | `ai_practitioner` | facultatif | coupée | l'auteur aurait-il envie de répondre ? |

Le régime des trois mondes de vente ne change pas.

Dans le monde `ai_practitioner`, un post sans ancrage disponible ouvre le mode
question : le commentaire est une question construite sur le seul contenu du
post, il n'affirme rien, et il porte sur ce que le post ne dit pas. Deux
contrôles de code remplacent les deux règles d'appartenance au corpus, qui n'ont
plus d'objet : le commentaire se termine sur une question directe, et il contient
au plus une phrase affirmative.

Six ancrages déjà vérifiés sont ouverts à ce monde : `a1`, `a2`, `a4`, `a6`,
`a7`, `a9`. Ils racontent ce qui a été vu en construisant. Restent fermés `a3` et
`a5`, propres au Sénégal, et `a8`, qui met en position de corriger l'auteur.

Aucun ancrage n'est créé, aucun principe n'est ajouté ni modifié.

## Ce que ce travail a réparé au passage

Ces quatre défauts existaient avant, et se déclenchaient tous sur ce feed.

`reader_world` n'était validé nulle part. Un monde mal orthographié produisait un
skip `corpus_vide_pour_ce_post`, indiscernable d'un post hors sujet. Un monde
absent du registre range désormais sous ERROR, avec `monde_lecteur_inconnu`.

Le découpage en phrases coupait sur le point d'un nombre décimal. « Gemini 3.8
Flash » comptait pour deux phrases, et tous les contrôles de comptage dérivaient
sur un feed plein de versions et de prix.

L'extraction des termes du post avalait la ponctuation qui suit un nombre.
« 12,930,300,000. » ne matchait pas « $12,930,300,000 » dans le commentaire, et
le commentaire était rejeté pour absence de terme propre au post.

La boucle de révision renvoyait au rédacteur des codes machine du type
`controle:does_not_end_on_question`. Elle renvoie maintenant une consigne rédigée.

Un `post_type` absent levait une exception et rangeait le post en panne. Le mode
question ne s'en sert pas, et le mode ancré retombait déjà sur la structure
`fond` : le repli est explicite, le post n'est plus une panne.

## Configuration

`qwen3.5:9b` est un modèle à raisonnement. Sans `OLLAMA_THINK=false`, il consomme
tout le budget de sortie dans le champ `thinking` et renvoie un `content` vide.
Le conteneur `pestel-brain-api` tournait dans cette configuration et ne pouvait
produire aucun commentaire. Vérifié avec
`python -m app.linkedin_comments.check_ollama_format` : `think=false` garde la
sortie structurée valide sur ce modèle. Réglé dans `docker-compose.db.yml` et
`.env.example`.

## Arbitrages d'Abdoulaye, 03/09/2026

**Desserrer la forme, miser sur le prompt.** Les bornes de la doctrine
commerciale, trois à cinq phrases et vingt mots, ont été écrites pour du français
devant un décideur. Sur des questions techniques en anglais elles coupaient
treize brouillons sur trente. Dans le mode question : trente mots par phrase, une
à quatre phrases, deux affirmations au maximum. Les chiffres annoncés au
rédacteur suivent les chiffres vérifiés par le code.

Deux règles restent contraintes, parce qu'elles seules empêchent le commentaire
générique : finir sur une vraie question, et porter un terme propre au post. Cet
arbitrage va contre le principe p2 du corpus, la remarque a été faite et écartée.

**Garder les posts personnels.** Rien n'est publié automatiquement, Abdoulaye
relit chaque brouillon. Aucune règle de monde ne les écarte. LCR-013 est classé
sans suite.

**Un workflow n8n par catégorie.** Le workflow `LinkedIn Apify to Ollama
Comments` est dédié à `ai_practitioner` et sera dupliqué par catégorie. Son nœud
`Run LinkedIn Comment Runtime` envoyait `reader_world: 'icp1'` en dur alors que
toutes les cibles actives sont classées `ai_practitioner` : chaque post repartait
donc en `anti_corpus:actualite_ia` ou `corpus_vide_pour_ce_post`. Corrigé le
03/09/2026.

## Ce qui reste à trancher par Abdoulaye

Le taux de brouillons est bas et le juge porte presque tous les refus. Il faut
regarder les sorties avant de décider si ce taux est le bon.

Rien pour l'instant. Le taux de brouillons après desserrage reste à mesurer.
