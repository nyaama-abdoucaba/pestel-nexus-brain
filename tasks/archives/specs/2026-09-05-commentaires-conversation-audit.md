# Commentaires conversationnels et audit multi-cibles

## Objectif
Produire des brouillons ICP1 naturels et pertinents sur le feed consultant du 5 septembre, sans inventer de vécu ni imposer une démonstration d'expertise. Conserver n8n → FastAPI → PostgreSQL et les contrats draft/skip/error.

## Décisions
- Une politique explicite par monde : ICP1 échange entre pairs ; les autres mondes gardent leurs critères propres.
- Le post prime sur le corpus. Le regard issu du CV éclaire la rédaction ; une expérience est facultative.
- Les contrôles bloquants portent sur des contraintes objectives. La pertinence, le ton et les affirmations relèvent du juge, sans obligation de question, contradiction ou nom propre.
- Chaque appel modèle conserve rôle, instructions, données, schéma, paramètres, réponse et durée, dans les diagnostics JSONB existants. Le contexte éditorial est versionné et conservé.
- Un brouillon est une proposition à relire, jamais une publication automatique.
- Le dry-run doit filtrer une catégorie/date, conserver un rapport JSON complet et ne pas écrire en base.

## Vérification et critères de sortie
1. Tests de régression : réussite sans ancrage, félicitation précise, contrôle langue/liens/longueur, révision bornée, rejet de vécu inventé, monde inconnu, isolation multi-cibles.
2. Audit persistant : contexte exact, appels et décisions récupérables en PostgreSQL ; aucune migration destructive.
3. Calibration réelle sur les 17 posts consultant (incluant doublon connu) avec rapport et appréciation éditoriale explicite. Au moins trois brouillons utilisables, pas seulement acceptés par le juge ; documenter les exclusions et limites.
4. Compatibilité des quatre mondes, du payload HTTP n8n existant et du digest vérifiée. Aucun envoi email ni commentaire LinkedIn pendant les tests.
5. API locale mise à jour et appel réel depuis le réseau n8n vérifié ; tests du dépôt et documentation alignés ; commit sur main.

## Hors périmètre
Déploiement d'une campagne, collecte de nouveaux contacts, envoi de DM et activation des workflows planifiés. Les taux de réponse et de connexion nécessitent des interactions réelles ultérieures.
