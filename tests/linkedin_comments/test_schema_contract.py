from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_comment_runs_schema_matches_runtime_outcomes():
    schema = (REPO_ROOT / "db" / "init" / "050_linkedin_comment_runs.sql").read_text()

    assert "status IN ('draft', 'skip', 'error')" in schema
    assert "status <> 'draft'" in schema
    assert "jsonb_typeof(diagnostics) = 'object'" in schema


def test_comment_runs_migration_maps_legacy_statuses():
    migration = (
        REPO_ROOT / "db" / "migrations" / "2026-09-01-linkedin-comment-runs-v2.sql"
    ).read_text()

    assert "WHEN 'ready_for_review' THEN 'draft'" in migration
    assert "WHEN 'rejected' THEN 'skip'" in migration
    assert "WHEN 'needs_human_review' THEN 'error'" in migration
    assert "WHEN 'failed' THEN 'error'" in migration
    assert "jsonb_typeof(diagnostics) = 'array'" in migration
    assert "jsonb_typeof(diagnostics) = 'object'" in migration


def test_long_editorial_hypothesis_is_truncated_not_rejected():
    """Un champ de diagnostic trop long ne doit pas jeter un commentaire valide.

    Vu en conditions réelles le 03/09/2026 : un run sur trente rangé sous ERROR
    parce que le modèle avait été bavard sur un champ qui n'atteint jamais
    LinkedIn.
    """
    from app.linkedin_comments.contracts import DraftResult, SourceLanguage

    draft = DraftResult(
        comment="Quelle limite as-tu vue en premier ?",
        language=SourceLanguage.FRENCH,
        editorial_hypothesis="x" * 600,
    )
    assert len(draft.editorial_hypothesis) == 280
    assert draft.editorial_hypothesis.endswith("...")
    assert draft.comment == "Quelle limite as-tu vue en premier ?"
