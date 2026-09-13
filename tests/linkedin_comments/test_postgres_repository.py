"""Le dépôt PostgreSQL ne doit lire que des champs qui existent encore.

Pourquoi ce fichier existe. Le 05/09/2026, `save()` lisait toujours
`result.preselected_ids`, un champ du sélecteur d'ancrages supprimé la veille.
Ce champ n'est lu qu'à la toute fin, donc l'erreur frappait TOUTES les
exécutions passées par l'API, y compris celles qui avaient produit un bon
commentaire. FastAPI renvoyait 500, et n8n affichait « Response body is not
valid JSON » seize fois de suite, sans jamais nommer la vraie cause.

Aucun test ne touchait cet adaptateur. On remplace donc la connexion par un
curseur factice : le test vérifie la construction du payload, pas PostgreSQL.
"""
from __future__ import annotations

from contextlib import contextmanager
from uuid import uuid4

import pytest

from app.infrastructure.postgres.linkedin_comment_repository import (
    PostgresLinkedInCommentRepository,
)
from app.linkedin_comments.contracts import (
    CommentRunResult,
    RunOutcome,
    SourceLanguage,
)


class FakeCursor:
    def __init__(self) -> None:
        self.executed: list[tuple] = []

    def execute(self, sql: str, params: tuple) -> None:
        self.executed.append((sql, params))


class RepoWithFakeCursor(PostgresLinkedInCommentRepository):
    def __init__(self) -> None:
        super().__init__(database_url="postgresql://factice/factice")
        self.cursor = FakeCursor()

    @contextmanager
    def _transaction(self):
        yield self.cursor


def _resultat(outcome: RunOutcome) -> CommentRunResult:
    return CommentRunResult(
        linkedin_post_id=uuid4(),
        outcome=outcome,
        reason_code=None if outcome is RunOutcome.DRAFT else "hors_sujet_professionnel",
        source_language=SourceLanguage.FRENCH,
        reader_world="icp1",
        comment_mode="principe",
        domaines=["ingenierie_ia"],
        comment_text="Un commentaire." if outcome is RunOutcome.DRAFT else None,
        model="qwen3.5:9b",
    )


@pytest.mark.parametrize("outcome", list(RunOutcome))
def test_save_ne_lit_que_des_champs_declares(outcome: RunOutcome) -> None:
    """Un champ retiré du contrat ne doit plus jamais casser la sauvegarde.

    `save()` est appelé sur les trois issues. Si l'une d'elles lève, le moteur
    perd aussi les exécutions réussies.
    """
    repo = RepoWithFakeCursor()

    repo.save(_resultat(outcome))

    assert len(repo.cursor.executed) == 1
    _, params = repo.cursor.executed[0]
    assert params[2] == outcome.value


def test_les_diagnostics_gardent_la_trace_du_routage() -> None:
    """`domaines` et `comment_mode` expliquent après coup le régime d'écriture."""
    repo = RepoWithFakeCursor()

    repo.save(_resultat(RunOutcome.DRAFT))

    _, params = repo.cursor.executed[0]
    diagnostics = params[7].obj
    assert diagnostics["domaines"] == ["ingenierie_ia"]
    assert diagnostics["comment_mode"] == "principe"
    assert diagnostics["reader_world"] == "icp1"
