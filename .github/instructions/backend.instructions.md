---
applyTo: "app/**/*.py"
---

- Préserve la séparation `interfaces -> application -> workflows -> infrastructure`.
- Un module métier ne doit pas accéder directement aux clients externes si un adapter existe déjà.
- Quand tu ajoutes une logique de flux, mets-la dans `workflows/target_comment` ou `workflows/newsjacking_post`.
- Quand tu ajoutes une règle métier stable, mets-la dans `domain/editorial`.
