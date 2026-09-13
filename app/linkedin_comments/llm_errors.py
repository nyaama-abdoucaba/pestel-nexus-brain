"""Exceptions partagées par les deux clients LLM (ollama_client / ollama_anthropic).

Une seule définition : le runtime et les routes API doivent pouvoir rattraper
ces erreurs quel que soit le transport choisi (LLM_TRANSPORT).
"""

from __future__ import annotations


class OllamaUnavailable(RuntimeError):
    """Ollama est indisponible ou ne répond pas au healthcheck."""


class LlmResponseError(RuntimeError):
    """La réponse LLM n'est pas exploitable par le runtime."""
