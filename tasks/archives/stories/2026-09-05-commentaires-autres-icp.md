# Story — Adapter les commentaires aux autres ICP

**Statut : à réaliser. Document fonctionnel uniquement, aucune implémentation demandée.**

## User story

En tant qu'Abdoulaye, je veux disposer de brouillons adaptés aux cadres en organisation, aux décideurs d'équipes de développement et aux responsables de projets IA en production, afin de participer naturellement à leurs discussions et de reconnaître les occasions commerciales pertinentes, sans mélanger leurs besoins avec ceux du consultant ICP1.

## Objectif et limites

Le commentaire ouvre un échange entre professionnels. Il doit donner envie de poursuivre la discussion, sans transformer chaque publication en diagnostic ou en présentation d'offre.

Le parcours d'Abdoulaye nourrit son regard ; il n'impose pas une anecdote. Les règles rigides du playbook — contre-exemple obligatoire, reconnaissance sans félicitation, question finale systématique — ne sont pas reprises comme obligations, conformément à l'orientation retenue dans la conversation.

Cette story prépare les autres segments. Elle ne demande ni lancement de campagne, ni collecte supplémentaire, ni publication, ni connexion, ni DM automatique. L'architecture existante reste n8n → FastAPI → PostgreSQL.

## Les trois segments à distinguer

| Segment | À qui répond-on ? | Ce que l'on cherche à comprendre | Relation avec l'offre |
|---|---|---|---|
| **ICP1-bis — cadre en organisation** | Responsable métier ou d'équipe en banque, assurance, télécom, agro-industrie, ONG ou administration | Ses priorités, les pratiques de l'équipe, les conditions d'adoption et de transmission | Atelier 1 pour une équipe ; décision et budget différents de l'achat individuel |
| **ICP2 — équipe utilisant déjà Claude Code** | Lead, CTO, dirigeant d'agence ou d'ESN, associé technique ; parfois un développeur utilisateur | Le passage de l'usage individuel à une pratique collective : revue, partage, autonomie et fiabilité | Atelier 2 ; lien possible avec une activation, à qualifier séparément |
| **ICP3 — équipe portant un projet IA en production** | CTO, responsable technique ou de plateforme, responsable produit technique | Le projet réel, les usages attendus et les arbitrages de mise en service | Atelier 3 ; achat d'entreprise et cycle plus long |

Un titre ne suffit pas. Un CTO peut relever d'ICP2, d'ICP3 ou d'aucun des deux selon son projet. Le développeur qui utilise l'outil n'est pas nécessairement le décideur ni le payeur.

Les praticiens IA suivis pour apprendre ou gagner en visibilité restent une relation distincte. Un expert qui répond à un commentaire ne devient pas automatiquement un prospect.

## Comportement attendu par segment

### ICP1-bis — Échanger sur le travail d'une équipe

Le commentaire peut porter sur une décision, une réussite collective, une façon de transmettre ou un changement de pratique. Il ne suppose ni résistance au changement, ni budget disponible, ni problème de productivité.

Le regard stratégie et organisation d'Abdoulaye est pertinent ; le détour par l'IA reste facultatif.

**Exemple fictif :** une responsable explique avoir associé les agences pilotes à la conception d'une procédure.

> Le fait d'associer les agences pilotes dès la conception me plaît. Quelle proposition venue du terrain a le plus changé la version finale ?

**Signal à explorer si la conversation se poursuit :** la personne exprime un besoin collectif et précise son rôle dans la décision. Le budget et l'échéance restent inconnus tant qu'ils ne sont pas exprimés.

### ICP2 — S'intéresser à une pratique technique collective

Le commentaire suit les choix concrets décrits dans le post : revue, configuration partagée, tests, intégration ou transmission. Il peut apprécier un choix ou demander un éclairage, sans chercher systématiquement un défaut.

Il ne suppose pas que le lecteur utilise Claude Code parce qu'il est développeur. Il ne lui explique pas son métier et n'invente pas une expérience technique d'Abdoulaye.

**Exemple fictif :** un lead raconte comment son équipe partage ses consignes Claude Code.

> Vous faites évoluer les consignes à partir des revues de code : cela donne un support concret aux échanges d'équipe. Comment choisissez-vous celles qui méritent d'être partagées ?

**Signal à explorer :** un usage déjà établi et un besoin collectif explicite. Distinguer ensuite apprentissage de l'équipe et accompagnement d'une mise en place ; ne pas proposer les deux offres par réflexe.

### ICP3 — Comprendre le projet et ses arbitrages

Le commentaire peut porter sur les utilisateurs, une décision de lancement, la mesure de qualité, les coûts ou l'organisation du service. Il n'exige pas de ramener chaque publication au RAG, aux évaluations ou au tool use.

Un prototype présenté publiquement n'est pas la preuve d'un échec en production. Une annonce ne prouve pas non plus les résultats obtenus.

**Exemple fictif :** une équipe décrit un pilote d'assistant limité à un premier groupe d'utilisateurs.

> Le périmètre limité du pilote laisse de la place pour apprendre des usages réels. Quel retour utilisateur vous aiderait le plus à décider de la suite ?

**Signal à explorer :** un projet identifié, une responsabilité dans sa réalisation et un besoin exprimé. Le format de cinq jours ne doit pas être proposé avant de comprendre les contraintes de l'équipe.

Ces exemples illustrent des possibilités, pas des gabarits obligatoires. Un bon commentaire peut aussi être une appréciation sans question.

## Règles communes de rédaction

1. Répondre à un détail réel du post et respecter son ton.
2. Choisir librement entre appréciation précise, accord développé, rapprochement, question ou réserve argumentée.
3. Utiliser seulement les expériences vérifiées lorsqu'un vécu personnel est évoqué. Une opinion ou une hypothèse clairement formulée reste possible sans anecdote.
4. Ne pas prétendre avoir consulté une pièce jointe ou une source absente du contexte.
5. Ne pas diagnostiquer un problème, un budget ou une intention d'achat à partir du seul rôle de la personne.
6. Ne pas intégrer d'offre, de lien commercial ou de demande de rendez-vous au commentaire.
7. Préférer un brouillon court et naturel à une structure remplie artificiellement.
8. Conserver la relecture et la publication manuelles. Une abstention justifiée vaut mieux qu'un commentaire forcé.

## Reconnaissance et qualification

Pour les futures conversations, distinguer les états suivants sans les confondre :

- **Profil potentiellement pertinent** : rôle ou contexte compatible, besoin non confirmé.
- **Interaction observée** : réponse ou échange réel ; pas une preuve d'achat.
- **Besoin exprimé** : difficulté, projet ou objectif formulé par la personne.
- **Occasion à qualifier** : lien plausible avec une offre, rôle décisionnel et calendrier à préciser.

La présence de deux personnes sous le même post ne prouve pas qu'elles ont vu leurs commentaires respectifs. Ne pas marquer une personne comme « tiède » sur cette seule base.

Dans les documents fournis, septembre donne la priorité à l'atelier 1 ; ICP2 et ICP3 servent surtout à reconnaître les conversations entrantes. Le playbook mentionne aussi la vente d'activations : l'arbitrage entre ces priorités devra être explicité avant une campagne dédiée. Cette story n'en lance aucune.

## Compatibilité et audit attendus pour une future réalisation

- Une catégorie de collecte et un ICP éditorial restent deux informations différentes.
- Conserver les identifiants existants quand ils correspondent au besoin : `icp1bis` pour le cadre, `dev` pour ICP2. ICP3 devra recevoir une politique explicite ; ne pas le faire passer silencieusement pour `dev`.
- Ne pas modifier le comportement ICP1 pour introduire un autre segment.
- Conserver, pour chaque proposition, le segment retenu, le point du post visé, les sources personnelles éventuellement utilisées et le motif d'acceptation ou de rejet.
- Un traitement destiné à une autre cible ou à une nouvelle politique ne doit pas être bloqué par l'historique d'un traitement différent.
- Ne pas déduire une qualification commerciale du simple verdict du juge éditorial.

## Critères d'acceptation

- [ ] Pour chacun des trois segments, une petite sélection de posts réels permet de relire plusieurs formes de commentaires, avec et sans question.
- [ ] Abdoulaye reconnaît sa voix et peut publier les brouillons retenus sans inventer une expérience ou réécrire entièrement leur angle.
- [ ] Les réponses restent pertinentes même lorsque le post ne parle pas directement d'IA.
- [ ] Un développeur utilisateur n'est pas automatiquement traité comme acheteur ; un CTO n'est pas automatiquement orienté vers ICP3.
- [ ] Le système sait conserver une cible incertaine plutôt que fabriquer une qualification.
- [ ] Les félicitations précises, les opinions et les questions sincères ne sont pas rejetées faute d'anecdote personnelle.
- [ ] Les expériences inventées, les offres déguisées et les questions auxquelles le post répond déjà sont écartées ou corrigées.
- [ ] Les raisons des décisions sont lisibles et le traitement des cibles existantes reste compatible.
- [ ] Aucun envoi ni aucune publication automatique ne sont introduits.

## Hors périmètre et questions ouvertes

Aucun code, changement de workflow, migration PostgreSQL, déploiement, tarification ou nouveau programme de formation dans cette story.

À préciser au moment de sa réalisation : exemples réels par segment, vocabulaire préféré d'Abdoulaye, priorité commerciale des activations et manière de conserver les retouches humaines.

Les chiffres de conversion, prérequis de cours et affirmations de marché des documents fournis n'ont pas été vérifiés ici. Ils ne constituent ni des garanties ni des critères d'acceptation de cette story.

## Sources

- Document fourni : « 00 — LINKEDIN : le playbook ».
- Document fourni : « 05 — ICP par atelier : qui achète quoi ».
- Orientation de cette conversation : élargir les commentaires, participer à la discussion et laisser le parcours nourrir le regard sans anecdote obligatoire.
