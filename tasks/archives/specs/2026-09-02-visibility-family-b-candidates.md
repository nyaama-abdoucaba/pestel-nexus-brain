# Spec — Candidats LinkedIn famille B

**Date** : 2026-09-02  
**Statut** : prêt à appliquer manuellement  

## Objectif

Préparer, sans l'exécuter, un seed idempotent des cibles LinkedIn retenues
manuellement : pages « famille B — se faire voir » et consultants à vendre.

## Contraintes

- Toutes les cibles restent `candidate` avec `scrape_enabled = false`.
- Les catégories sont créées ou mises à jour de façon idempotente.
- Les URLs sont enregistrées sans `/` final ; cela évite de créer deux fois la
  même cible pour une URL équivalente.
- La catégorie métier des personnes est `consultant`.
- Les doublons probables DigitalAfrica / Digital Afrika ne sont pas chargés.
- La migration `2026-09-02-linkedin-target-url-kinds.sql` autorise les URLs
  LinkedIn `/in/`, `/company/` et `/school/`.
