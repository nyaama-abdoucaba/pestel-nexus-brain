import os

from pydantic_settings import BaseSettings, SettingsConfigDict


def _parse_optional_bool(raw: str) -> bool | None:
    """"" -> None (pas de préférence), "true"/"false" -> bool. Défaut sûr : None."""
    normalized = raw.strip().lower()
    if normalized in ("", "none", "null"):
        return None
    if normalized in ("1", "true", "yes", "on"):
        return True
    if normalized in ("0", "false", "no", "off"):
        return False
    raise ValueError(f"OLLAMA_THINK invalide: {raw!r} (attendu vide, true ou false)")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = os.getenv("DATABASE_URL", "")
    ollama_url: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "gemma4:31b-cloud")
    ollama_timeout_seconds: int = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "60"))
    # "ollama_native" (défaut) = champ `format` natif d'Ollama, JSON Schema en
    # contrainte de décodage — la garantie la plus forte.
    # "anthropic_compat" = SDK `anthropic` sur l'endpoint /v1/messages
    # d'Ollama, structuré via tool_use. Ollama ne supporte pas `tool_choice`
    # sur cette couche : moins de garantie, à valider empiriquement sur ce
    # modèle avant de s'y fier en production. Voir ollama_anthropic.py.
    llm_transport: str = os.getenv("LLM_TRANSPORT", "ollama_native")
    # None (défaut) = on ne force pas `think` dans la requête Ollama. Piège connu
    # (github.com/ollama/ollama/issues/15260) : think=false peut casser `format`
    # sur certains modèles Gemma. Ne mettre OLLAMA_THINK=false qu'après avoir
    # fait tourner `python -m app.linkedin_comments.check_ollama_format` sur ce
    # modèle précis et constaté que le JSON structuré reste valide.
    ollama_think: bool | None = _parse_optional_bool(os.getenv("OLLAMA_THINK", ""))
    comment_analysis_max_tokens: int = int(os.getenv("COMMENT_ANALYSIS_MAX_TOKENS", "1200"))
    comment_writer_max_tokens: int = int(os.getenv("COMMENT_WRITER_MAX_TOKENS", "700"))
    comment_judge_max_tokens: int = int(os.getenv("COMMENT_JUDGE_MAX_TOKENS", "800"))

settings = Settings()
