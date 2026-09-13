"""Vérifie tôt le piège think=false / format cassé (ollama/ollama#15260).

Usage :
    python -m app.linkedin_comments.check_ollama_format

À lancer une fois par modèle, avant le premier dry-run. N'active jamais
OLLAMA_THINK=false en configuration si `think_false` sort à False ici.
"""

from __future__ import annotations

import sys

from app.config import settings
from app.linkedin_comments.ollama_client import diagnose_think_format_bug


def main() -> int:
    print(f"Modèle : {settings.ollama_model}  ({settings.ollama_url})")
    results = diagnose_think_format_bug(settings.ollama_url, settings.ollama_model, settings.ollama_timeout_seconds)
    print(f"  think par défaut (non forcé) -> JSON valide : {results['think_default']}")
    print(f"  think=false                  -> JSON valide : {results['think_false']}")
    print()

    if not results["think_default"]:
        print(
            "⚠️  Même sans forcer `think`, la sortie structurée n'est pas valide. "
            "Le problème n'est pas le piège think=false : vérifier Ollama, le modèle, "
            "et la version d'Ollama avant d'aller plus loin."
        )
        return 1

    if results["think_false"]:
        print("OK — think=false peut être activé dans la configuration (OLLAMA_THINK=false) sans casser `format`.")
        return 0

    print(
        "⚠️  Piège confirmé (ollama/ollama#15260) : think=false casse la sortie structurée sur ce modèle.\n"
        "    Laisser OLLAMA_THINK vide (défaut) dans la configuration — ne jamais mettre OLLAMA_THINK=false."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
