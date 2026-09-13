# Fixtures de dry-run

Ces posts servent à faire tourner `dry_run.py --fixtures` sans base de
données, pour un premier tour de fumée sur une machine qui a Ollama et le
modèle Gemma configurés (voir `check_ollama_format.py` en premier).

**Ce ne sont pas des posts réels du feed cible.** Le critère d'acceptation de
la mission (« trois brouillons que je publierais tels quels, sur des posts
francophones réels de mon feed cible ») ne peut être vérifié qu'avec de vrais
posts archivés — via `dry_run.py --db` sur la base déjà peuplée par le moteur
n8n, ou via un fichier `--fixtures` qu'Abdoulaye fournit lui-même au même
format.

- `mpme-rao-dekkando` : le seul post réel du lot. Texte transcrit du worked
  example de la fiche 07 du coffre éditorial (le post « accompagnement des
  MPME », terrain à Rao). La fiche note qu'il a deux mois et qu'il « sert
  d'étalonnage, pas de cible » : il n'est ici que pour vérifier que le moteur
  retrouve bien l'ancrage `a3`/`a5` attendu, jamais pour produire un vrai
  brouillon à publier.
- Les autres entrées sont synthétiques, calquées sur les cas écrits du
  playbook (angle célébration) avec des noms et organisations fictifs, pour
  couvrir plusieurs `post_type` lors du test de fumée.
