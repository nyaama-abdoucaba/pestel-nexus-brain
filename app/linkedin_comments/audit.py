"""Trace des appels modèle, sans stockage ni dépendance à FastAPI.

Les prompts et réponses exacts permettent de comprendre un verdict après une
évolution du corpus. Ils contiennent les posts et faits autorisés, aucun secret
de connexion. Le repository persiste cette trace dans les diagnostics JSONB.
"""
from __future__ import annotations

import time
from typing import Any

from pydantic import BaseModel, Field


class ModelCallTrace(BaseModel):
    stage: str
    system: str
    user: str
    output_schema: dict[str, Any]
    max_tokens: int
    temperature: float
    response: str | None = None
    output_tokens: int = 0
    duration_ms: int = 0
    error_type: str | None = None


def complete_with_trace(llm, traces: list[ModelCallTrace], *, stage: str, **request):
    trace = ModelCallTrace(stage=stage, output_schema=request['schema'],
                           **{k: v for k, v in request.items() if k != 'schema'})
    traces.append(trace)
    started = time.monotonic()
    try:
        completion = llm.complete(**request)
        trace.response = completion.text
        trace.output_tokens = completion.output_tokens
        return completion
    except Exception as exc:
        trace.error_type = type(exc).__name__
        raise
    finally:
        trace.duration_ms = round((time.monotonic() - started) * 1000)
