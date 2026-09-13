"""Client compatible API Anthropic — parle à l'endpoint /v1/messages d'Ollama.

Ollama expose depuis 2025 une couche de compatibilité Anthropic
(https://docs.ollama.com/api/anthropic-compatibility) : le SDK `anthropic`
officiel peut donc pointer vers Ollama, et c'est ce que fait ce client.

⚠️ Deux limites documentées par Ollama lui-même, qui changent la garantie de
fiabilité par rapport au client natif (ollama_client.py, champ `format`) :

  - `tool_choice` n'est PAS supporté sur cette couche : impossible de forcer
    le modèle à répondre via l'outil. On ne peut que l'y pousser fortement
    par consigne et en ne proposant qu'un seul outil.
  - Aucun équivalent du champ `format` (contrainte de décodage au niveau du
    modèle) n'existe ici : la seule structure garantie vient de l'appel
    d'outil (tool_use) — si le modèle répond en texte libre à la place (ce
    qu'il peut faire, faute de tool_choice), ce client retombe sur un
    filet de secours en texte, moins fiable.
  - Le tool-calling de la famille Gemma sous Ollama est lui-même signalé
    comme peu abouti par la communauté (github.com/ollama/ollama/issues/9941)
    au moment où ce module est écrit : à vérifier empiriquement sur le
    modèle réel, comme pour le piège think=false d'ollama_client.py.

Les deux clients (`ollama_client.OllamaClient` et
`ollama_anthropic.AnthropicOllamaClient`) exposent la même interface
(`healthcheck`, `complete(system=, user=, max_tokens=, temperature=, schema=)`
-> `Completion`) et sont interchangeables dans `LinkedInCommentRuntime`. Le
choix se fait via `LLM_TRANSPORT` dans la configuration (voir config.py).
"""

from __future__ import annotations

import inspect
import json
from dataclasses import dataclass
from urllib.error import URLError
from urllib.request import urlopen

from app.linkedin_comments.llm_errors import LlmResponseError, OllamaUnavailable


@dataclass(frozen=True)
class Completion:
    text: str
    input_tokens: int = 0
    output_tokens: int = 0


_TOOL_NAME = "submit_structured_response"


class AnthropicOllamaClient:
    """Structure la sortie via tool_use, sur l'endpoint /v1/messages d'Ollama.

    `complete()` garde la même signature que `OllamaClient` (schéma inclus)
    pour rester interchangeable : le JSON Schema devient l'`input_schema`
    d'un unique outil, et l'appel d'outil devient le texte JSON renvoyé.
    """

    def __init__(self, base_url: str, model: str, timeout_seconds: int = 60, client: object | None = None):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds
        self._client = client

    def healthcheck(self) -> None:
        try:
            with urlopen(f"{self.base_url}/api/tags", timeout=self.timeout_seconds) as response:
                if response.status != 200:
                    raise OllamaUnavailable(f"Ollama returned HTTP status {response.status}.")
        except (URLError, TimeoutError, OSError) as exc:
            raise OllamaUnavailable("Ollama is not responding.") from exc

    def complete(
        self, *, system: str, user: str, max_tokens: int, temperature: float, schema: dict
    ) -> Completion:
        client = self._client or self._build_client()
        tool = {
            "name": _TOOL_NAME,
            "description": "Renvoie la réponse structurée attendue, conforme exactement au schéma fourni.",
            "input_schema": schema,
        }
        forced_system = (
            f"{system}\n\nRéponds en appelant l'outil `{_TOOL_NAME}` avec les champs attendus — "
            "n'écris aucun texte hors de cet appel d'outil."
        )
        create_kwargs: dict = {
            "model": self.model,
            "max_tokens": max_tokens,
            "system": forced_system,
            "messages": [{"role": "user", "content": user}],
            "tools": [tool],
        }
        if "temperature" in inspect.signature(client.messages.create).parameters:
            create_kwargs["temperature"] = temperature

        try:
            message = client.messages.create(**create_kwargs)
        except OllamaUnavailable:
            raise
        except Exception as exc:  # connexion / HTTP vers Ollama
            raise OllamaUnavailable(f"Appel Ollama (API Anthropic) impossible : {exc.__class__.__name__}") from exc

        tool_call = next(
            (
                block for block in message.content
                if getattr(block, "type", None) == "tool_use" and getattr(block, "name", None) == _TOOL_NAME
            ),
            None,
        )
        if tool_call is not None:
            text = json.dumps(tool_call.input, ensure_ascii=False)
        else:
            # tool_choice n'est pas supporté par Ollama : le modèle a pu répondre
            # en texte libre malgré la consigne. Filet de secours, pas une garantie —
            # c'est exactement la fiabilité perdue par rapport au champ `format` natif.
            text = "\n".join(
                block.text for block in message.content
                if getattr(block, "type", None) == "text" and getattr(block, "text", "")
            ).strip()

        if not text:
            raise LlmResponseError("LLM returned neither a tool call nor text.")

        usage = getattr(message, "usage", None)
        return Completion(
            text=text,
            input_tokens=int(getattr(usage, "input_tokens", 0) or 0),
            output_tokens=int(getattr(usage, "output_tokens", 0) or 0),
        )

    def _build_client(self) -> object:
        try:
            from anthropic import Anthropic
        except ImportError as exc:
            raise RuntimeError("Le package anthropic est requis pour AnthropicOllamaClient.") from exc
        self._client = Anthropic(base_url=self.base_url, api_key="ollama")
        return self._client
