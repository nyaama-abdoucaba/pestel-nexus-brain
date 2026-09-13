---
name: api-integration
description: Intégrer une API externe de manière isolée, testée et observable
disable-model-invocation: false
---

# But
- Ajouter un client API fiable sans polluer la logique métier.

# Déclencheur
- Nouveau provider, nouvel appel externe, nouvelle dépendance réseau.

# Entrées attendues
- Auth, endpoints, timeouts, limites, mapping métier attendu.

# Procédure
1. Définir le contrat interne.
2. Implémenter le client dans `infrastructure/`.
3. Mapper les erreurs externes vers des erreurs internes explicites.
4. Ajouter les tests essentiels.
5. Vérifier l’absence de secrets en dur.

# Quality gates
- Client isolé
- Erreurs explicites
- Vérification exécutée

# Output attendu
- Adapter externe + tests + doc minimale

# Stop conditions
- Si le contrat externe est ambigu, bloquer avant l’implémentation.
