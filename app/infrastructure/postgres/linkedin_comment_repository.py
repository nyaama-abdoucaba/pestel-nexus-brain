from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Any, Generator

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from app.linkedin_comments.contracts import CommentRunResult, LinkedInPost


class PostgresCommentRepositoryError(RuntimeError):
    """Erreur d'accès PostgreSQL sans exposer DATABASE_URL."""


class PostgresLinkedInCommentRepository:
    def __init__(self, database_url: str | None = None):
        self.database_url = database_url or os.getenv("DATABASE_URL", "")

    @contextmanager
    def _transaction(self) -> Generator[psycopg.Cursor, None, None]:
        if not self.database_url:
            raise PostgresCommentRepositoryError("DATABASE_URL est absente.")
        try:
            with psycopg.connect(self.database_url, row_factory=dict_row) as connection:
                with connection.cursor() as cursor:
                    yield cursor
        except psycopg.Error as exc:
            raise PostgresCommentRepositoryError(f"PostgreSQL error: {exc.__class__.__name__}") from exc

    def load_post(self, post_id: str) -> LinkedInPost | None:
        with self._transaction() as cursor:
            cursor.execute(
                """
                SELECT p.id, p.text, p.url, p.content_hash, t.name AS author_name, t.why_follow
                FROM linkedin_posts p
                JOIN linkedin_targets t ON t.id = p.linkedin_target_id
                WHERE p.id = %s
                """,
                (post_id,),
            )
            row: dict[str, Any] | None = cursor.fetchone()
        return LinkedInPost.model_validate(row) if row else None

    def save(self, result: CommentRunResult) -> None:
        """Persiste le run avec `status = result.outcome`.

        La colonne garde son nom historique, mais son vocabulaire suit le
        contrat runtime actuel : `draft`, `skip` ou `error`. Le détail lisible
        de la décision reste dans `diagnostics`.
        """
        payload = result.model_dump(mode="json")
        diagnostics_payload = {
            "reason_code": result.reason_code,
            "reader_world": result.reader_world,
            "post_type": payload["post_type"],
            # Trace du routage : quels domaines le post a touchés, et sous quel
            # régime le commentaire a été écrit. Ces deux champs expliquent après
            # coup pourquoi un principe a servi, ou pourquoi aucun n'a servi.
            # Ne lire ici que des champs déclarés dans CommentRunResult : un
            # attribut disparu casse la sauvegarde de TOUTES les exécutions,
            # succès compris (incident du 05/09/2026, seize erreurs).
            "domaines": payload["domaines"],
            "comment_mode": result.comment_mode,
            "details": payload["diagnostics"],
            "editorial_context": payload["editorial_context"],
            "model_calls": payload["model_calls"],
        }
        with self._transaction() as cursor:
            cursor.execute(
                """
                INSERT INTO linkedin_comment_runs (
                    id, linkedin_post_id, status, source_language, comment_text,
                    analysis_payload, revisions_payload, diagnostics, model_name, prompt_version, content_hash
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    str(result.run_id),
                    str(result.linkedin_post_id),
                    result.outcome.value,
                    result.source_language.value if result.source_language else None,
                    result.comment_text,
                    Jsonb(payload["analysis"]) if payload["analysis"] is not None else None,
                    Jsonb(payload["revisions"]),
                    Jsonb(diagnostics_payload),
                    result.model,
                    result.prompt_version,
                    result.content_hash,
                ),
            )
