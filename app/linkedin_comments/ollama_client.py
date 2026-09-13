"""Client Ollama natif — contrainte dure du runtime.

Modèle local, Ollama, famille Gemma, sur Mac. Pas d'API Anthropic, donc pas de
tool_use : la sortie structurée passe par le champ `format` d'Ollama
(/api/chat), avec un JSON Schema complet sur chaque appel. C'est ce module qui
remplace l'ancien pont via le SDK `anthropic` (ollama_anthropic.py), qui
n'exposait aucun moyen de passer `format` et laissait la conformité JSON au
seul texte du prompt.

⚠️ Piège connu (github.com/ollama/ollama/issues/15260) : sur certains modèles
de la famille Gemma, `think=false` casse la sortie structurée du champ
`format` — le JSON sort bon en mode pensée, cassé sans. Par défaut, ce client
NE force PAS `think` : il laisse le paramètre absent de la requête plutôt que
de risquer la combinaison cassée. N'active `think=False` en configuration
qu'après avoir fait tourner `diagnose_think_format_bug()` sur ce modèle précis
et constaté que le JSON reste valide dans les deux modes.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.linkedin_comments.llm_errors import LlmResponseError, OllamaUnavailable


def _body_of(exc: HTTPError) -> str:
    """Le corps d'une réponse d'erreur, borné, jamais au prix d'une seconde panne."""
    try:
        return exc.read().decode("utf-8", "replace")[:500]
    except Exception:  # noqa: BLE001 — un diagnostic ne doit jamais lever
        return "corps illisible"


@dataclass(frozen=True)
class Completion:
    text: str
    input_tokens: int = 0
    output_tokens: int = 0


class OllamaClient:
    """Parle directement à /api/tags et /api/chat, sans intermédiaire.

    `complete()` prend un `schema` (JSON Schema) et le passe tel quel dans le
    champ `format` de la requête Ollama — c'est le mécanisme natif de sortie
    structurée, indépendant de tout `tool_use`.
    """

    def __init__(
        self,
        base_url: str,
        model: str,
        timeout_seconds: int = 60,
        think: bool | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.think = think

    def healthcheck(self) -> None:
        try:
            with urlopen(f"{self.base_url}/api/tags", timeout=self.timeout_seconds) as response:
                if response.status != 200:
                    raise OllamaUnavailable(f"Ollama returned HTTP status {response.status}.")
        except (URLError, TimeoutError, OSError) as exc:
            raise OllamaUnavailable("Ollama is not responding.") from exc

    def complete(
        self,
        *,
        system: str,
        user: str,
        max_tokens: int,
        temperature: float,
        schema: dict,
    ) -> Completion:
        payload: dict = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "format": schema,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        if self.think is not None:
            payload["think"] = self.think

        request = Request(
            f"{self.base_url}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                raw = response.read()
        except HTTPError as exc:
            # Ollama a répondu, et il a répondu non. `HTTPError` hérite de
            # `OSError` : sans cette branche, un refus explicite était rebaptisé
            # « did not respond » et son corps était jeté. On perdait la seule
            # phrase qui dit pourquoi (incident du 05/09/2026).
            raise OllamaUnavailable(
                f"Ollama a refusé /api/chat avec le code {exc.code} : {_body_of(exc)}"
            ) from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise OllamaUnavailable("Ollama did not respond to /api/chat.") from exc

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise LlmResponseError("Ollama returned a non-JSON envelope.") from exc

        text = (parsed.get("message") or {}).get("content", "")
        if not text:
            raise LlmResponseError("Ollama returned no content.")

        return Completion(
            text=text,
            input_tokens=int(parsed.get("prompt_eval_count") or 0),
            output_tokens=int(parsed.get("eval_count") or 0),
        )


_PROBE_SCHEMA = {
    "type": "object",
    "properties": {"ok": {"type": "boolean"}},
    "required": ["ok"],
}


def diagnose_think_format_bug(base_url: str, model: str, timeout_seconds: int = 60) -> dict[str, bool]:
    """Vérifie tôt le piège ollama/ollama#15260 sur CE modèle, avant tout dry-run.

    Envoie le même appel structuré avec think=<défaut du modèle> puis
    think=False, et rapporte pour chacun si la sortie respecte le schéma JSON
    demandé. Un modèle qui échoue sous think_false ne doit jamais être
    configuré avec think=False dans les settings du runtime.
    """
    results: dict[str, bool] = {}
    for label, think_value in (("think_default", None), ("think_false", False)):
        client = OllamaClient(base_url, model, timeout_seconds=timeout_seconds, think=think_value)
        try:
            completion = client.complete(
                system="Return JSON only, matching the schema exactly. No markdown.",
                user='Respond with {"ok": true}.',
                max_tokens=50,
                temperature=0.0,
                schema=_PROBE_SCHEMA,
            )
            parsed = json.loads(completion.text)
            results[label] = isinstance(parsed, dict) and parsed.get("ok") is True
        except Exception:
            results[label] = False
    return results
