# LCR-017 — La sauvegarde lisait un champ supprimé

**Statut** : done. Hotfix rétroactif, spec écrite après le correctif, conformément à la règle hotfix.

## Le symptôme

Digest du 05/09/2026 au soir : 16 posts, 0 brouillon, 16 erreurs, toutes avec le
même message n8n, `Response body is not valid JSON. Change "Response Format" to
Text`.

## La cause

`PostgresLinkedInCommentRepository.save()` lisait encore deux champs supprimés du
contrat la veille avec le corpus d'ancrages : `result.preselected_ids` et
`result.selection.selected_id`. `save()` est appelé par `_finish()`, donc sur les
trois issues. Chaque exécution levait `AttributeError`, FastAPI renvoyait une page
d'erreur HTML, et n8n n'avait plus de JSON à lire.

Le message de n8n décrit ce que n8n voit, jamais la cause. La cause était dans
`docker logs pestel-brain-api`.

Preuve directe : la dernière ligne écrite dans `linkedin_comment_runs` datait du
05/09 à 16 h 50. Les deux lots du soir n'ont rien sauvegardé du tout.

## Pourquoi aucun test ne l'a vu

`runtime.py` ne connaît que le `Protocol` `RunRepository`. Les 101 tests passaient
un faux dépôt, et aucun test ne couvrait l'adaptateur PostgreSQL. Cette
indépendance rend la suite rapide, et elle laissait cet adaptateur aveugle.

## Second défaut trouvé au passage

`OllamaClient.complete()` attrapait `HTTPError` dans la branche
`except (URLError, TimeoutError, OSError)`. `HTTPError` hérite de `OSError` : un
refus explicite d'Ollama, code et corps compris, était rebaptisé « Ollama did not
respond » et son message jeté. La branche dédiée nomme désormais le code et cite
le corps de la réponse.

## Fichiers touchés

- `app/infrastructure/postgres/linkedin_comment_repository.py` — `preselected_ids`
  et `selected_id` remplacés par `domaines`.
- `app/linkedin_comments/ollama_client.py` — `HTTPError` traité à part, code et
  corps conservés.
- `tests/linkedin_comments/test_postgres_repository.py` — nouveau. Curseur
  factice, `save()` vérifié sur les trois issues.

## Vérification

    ./scripts/verify.sh          # 105 passed

    curl -s -X POST http://localhost:8000/v1/linkedin-comment-runs \
      -H "Content-Type: application/json" \
      -d '{"linkedin_post_id":"<un id de linkedin_posts>","reader_world":"icp1"}' \
      -w "\nHTTP %{http_code}\n"

Résultat obtenu : HTTP 201 en 30 s, JSON valide, ligne écrite en base avec
`domaines = ["ingenierie_ia"]` et `comment_mode = principe`.

Le test a été validé à l'envers : la ligne fautive remise, les quatre cas
échouent, y compris le cas `draft`. Un commentaire réussi ne pouvait donc pas non
plus être sauvegardé.

## Reste à faire

1. Le délai du client Ollama vaut 60 s, celui du node n8n 180 s. Sous charge, un
   appel a mis 51 s. Marge trop courte.
2. `retryOnFail` du node n8n rejoue trois fois une réponse illisible, pendant que
   l'appel précédent continue de tourner côté API. Mécanisme probable de
   l'empilement observé à 22 h 12, neuf requêtes Ollama en vol. Non mesuré.
3. Le node `Build Digest` affiche encore un bloc `Sélection`, champ supprimé.
4. Le workflow praticiens IA n'a pas reçu la déduplication par `prompt_version`.
