# EPIC-CCAR-CC : configurer Claude Code pour le dépôt

**Statut** : validé par Abdoulaye le 2026-09-15
**Epic parent** : EPIC-CCAR, remplace les lots L1, L2 et L2b
**PRD source** : `docs/prd/2026-09-09-ccar-f-alignment-prd.md`, version 1.3, sections 9.3 et 9.6
**Domaine d'examen** : 3, configuration Claude Code et workflows, 20 % des points

## Ce que ce sous-epic doit obtenir

Une configuration Claude Code où chaque consigne est chargée au bon moment, où
chaque interdiction est appliquée par le client plutôt qu'espérée, et où la revue
de code tourne en session isolée avec une sortie lisible par machine.

## Pourquoi un sous-epic

Les notes d'Abdoulaye sur les chapitres 6, 7 et 8 du livre communautaire ont
montré quatre erreurs dans les exigences du domaine 3. La matière dépasse un lot
d'une demi-journée. Un sous-epic garde EPIC-CCAR lisible et donne à ce domaine son
propre suivi.

## Quand il sera fini

1. Les sept slices sont fusionnées par PR.
2. Les exigences F-3.1 à F-3.9 du PRD sont vérifiées par leurs critères.
3. Les six énoncés 3.1 à 3.6 de l'examen pointent chacun vers un artefact du dépôt.

## Les slices

L'ordre suit le risque. CCAR-001 retire la règle Git fausse avant qu'un agent ne
la lise. CCAR-002 pose les interdictions avant que les skills ne parcourent le
dépôt.

| Slice | Contenu dans le dépôt | Exigences | Énoncé | Chapitre | Statut |
|---|---|---|---|---|---|
| CCAR-001 | `CLAUDE.md` sans contradiction : règle Git, import de `AGENTS.md`, `CLAUDE.local.md` | F-3.1, F-3.2 | 3.1 | 6 | todo |
| CCAR-002 | permissions : `allow` obsolètes retirés, `deny` sur les données privées, `.env`, `git push --force` | F-3.3 | 3.1 | 6, § 11 | todo |
| CCAR-003 | règles `paths` : tests sans base ni modèle, `db/` sans personne nommée, `PROMPT_VERSION` à monter | F-3.4 | 3.3 | 6, § 8 à 10 | todo |
| CCAR-004 | skills migrées ; le contrôle des données publiables devient une skill `context: fork` ; `/verify` en commande | F-3.5, F-3.6 | 3.2 | 7 | todo |
| CCAR-005 | mode d'exécution noté dans chaque slice, avec les deux questions du chapitre 7 | F-3.7 | 3.4, 3.5 | 7 | transverse |
| CCAR-006 | revue voie A : `dontAsk`, `--max-budget-usd`, `structured_output`, sessions isolées, `--bare` avec Ollama | F-3.8 | 3.6 | 8 | todo |
| CCAR-007 | revue voie B : action officielle, `claude_args`, `id-token: write`, jeton d'abonnement | F-3.9 | 3.6 | 8 | todo |

CCAR-005 n'a pas de livraison propre. Elle s'exécute dans les six autres : chaque
slice porte une section « Mode d'exécution ».

## Les décisions métier à prendre à l'ouverture des slices

| Slice | Question posée à Abdoulaye |
|---|---|
| CCAR-001 | quelles consignes du `CLAUDE.md` projet sont des préférences personnelles, à déplacer dans `CLAUDE.local.md` |
| CCAR-001 | quelle consigne garder quand le `CLAUDE.md` projet et le `CLAUDE.md` utilisateur se contredisent |
| CCAR-002 | la liste exacte de ce qui est interdit |
| CCAR-006 | le plafond de dépense par revue |

## La méthode de révision

Chaque slice commence et finit par la même lecture.

1. Avant de coder : lire l'énoncé d'examen de la slice dans le guide officiel, puis
   la section correspondante des notes du livre.
2. Après la fusion : relire les deux, et répondre aux questions d'exemple du
   chapitre qui portent sur ce point.

## Les faits vérifiés sur lesquels cet epic repose

| Fait | Source | Vérifié le |
|---|---|---|
| un fichier importé par `@` se charge en entier au démarrage | documentation « memory » | 2026-09-15 |
| `/context` montre les fichiers chargés, `/memory` leurs emplacements | documentation « memory » | 2026-09-15 |
| deux `CLAUDE.md` contradictoires : Claude peut choisir l'un au hasard | documentation « memory » | 2026-09-15 |
| une skill personnelle l'emporte sur une skill projet du même nom | documentation « skills » | 2026-09-15 |
| `allowed-tools` accorde des droits, `disallowed-tools` en retire | documentation « skills » | 2026-09-15 |
| `--bare` n'accepte que `ANTHROPIC_API_KEY` ou `apiKeyHelper` | `claude --help`, version 2.1.260 | 2026-09-15 |
| `--permission-mode` accepte `dontAsk` | `claude --help`, version 2.1.260 | 2026-09-15 |
| `--max-turns` | absent de l'aide de la 2.1.260 | à vérifier dans CCAR-006 |
