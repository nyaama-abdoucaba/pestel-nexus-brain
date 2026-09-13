---
name: database-change
description: Modifier la base avec migration, compatibilité et rollback clair
disable-model-invocation: true
---

# But
- Faire évoluer le schéma sans casser la prod.

# Déclencheur
- Nouvelle table, nouvelle colonne, index, contrainte, migration de données.

# Entrées attendues
- Schéma actuel, changement demandé, contraintes de compatibilité.

# Procédure
1. Décrire la migration et le rollback.
2. Vérifier la compatibilité ancienne app / nouveau schéma.
3. Séparer ajout, migration et suppression si nécessaire.
4. Ajouter les tests d’intégration critiques.

# Quality gates
- Rollback explicable en trois phrases
- Pas d’action destructrice sans plan

# Output attendu
- Migration + adaptation applicative + doc de rollback

# Stop conditions
- Si le rollback n’est pas clair, ne pas implémenter.
