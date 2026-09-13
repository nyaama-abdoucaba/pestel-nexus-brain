---
name: debugging
description: Debugger un bug avec reproduction, test rouge, puis correctif minimal
disable-model-invocation: false
---

# But
- Corriger un bug sans guesswork.

# Déclencheur
- Bug report, régression, échec de vérification.

# Entrées attendues
- Symptôme, contexte, logs, reproduction connue ou partielle.

# Procédure
1. Reproduire le bug.
2. Localiser le point de vérité.
3. Écrire ou identifier un test rouge.
4. Corriger avec le plus petit diff crédible.
5. Exécuter `./scripts/verify.sh` ou la commande ciblée.

# Quality gates
- Test anti-régression présent
- Cause racine expliquée en une phrase

# Output attendu
- Correctif minimal + preuve de vérification

# Stop conditions
- Si la reproduction manque, demander des données au lieu de coder au hasard.
