"""Construit le bon client LLM selon `settings.llm_transport`.

Centralise le choix entre les deux transports interchangeables — voir
ollama_client.py et ollama_anthropic.py pour ce que chacun garantit.
"""

from __future__ import annotations

from app.config import Settings
from app.linkedin_comments.ollama_anthropic import AnthropicOllamaClient
from app.linkedin_comments.ollama_client import OllamaClient


def build_llm_client(settings: Settings):
    if settings.llm_transport == "anthropic_compat":
        return AnthropicOllamaClient(
            base_url=settings.ollama_url,
            model=settings.ollama_model,
            timeout_seconds=settings.ollama_timeout_seconds,
        )
    if settings.llm_transport == "ollama_native":
        return OllamaClient(
            base_url=settings.ollama_url,
            model=settings.ollama_model,
            timeout_seconds=settings.ollama_timeout_seconds,
            think=settings.ollama_think,
        )
    raise ValueError(
        f"LLM_TRANSPORT invalide: {settings.llm_transport!r} (attendu 'ollama_native' ou 'anthropic_compat')"
    )
