from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

UI_PATH = Path(__file__).resolve().parent.parent.parent / "ui"
if str(UI_PATH) not in sys.path:
    sys.path.insert(0, str(UI_PATH))


# ── DATABASE_URL absente ──────────────────────────────────────────────────────

def test_missing_database_url_raises(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    import importlib
    import postgres
    importlib.reload(postgres)
    with pytest.raises(postgres.UiPostgresError, match="DATABASE_URL"):
        postgres.get_connection()


# ── Erreur de connexion traduite sans fuite du secret ─────────────────────────

def test_connection_error_raises_ui_error(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:secret@localhost/db")
    import importlib
    import postgres
    importlib.reload(postgres)

    import psycopg
    with patch("psycopg.connect", side_effect=psycopg.OperationalError("connection refused")):
        with pytest.raises(postgres.UiPostgresError) as exc_info:
            postgres.get_connection()
    assert "secret" not in str(exc_info.value)
    assert "OperationalError" in str(exc_info.value) or "PostgreSQL" in str(exc_info.value)


# ── Transaction commit réussie ────────────────────────────────────────────────

def test_transaction_commit_on_success(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
    import importlib
    import postgres
    importlib.reload(postgres)

    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cur)
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

    with patch("postgres.get_connection", return_value=mock_conn):
        with postgres.transaction() as cur:
            cur.execute("SELECT 1")

    mock_cur.execute.assert_called_once_with("SELECT 1")


# ── Transaction rollback sur erreur ──────────────────────────────────────────

def test_transaction_rollback_on_error(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
    import importlib
    import postgres
    importlib.reload(postgres)

    import psycopg

    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cur)
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

    def raise_error(*args, **kwargs):
        raise psycopg.errors.DatabaseError("boom")

    mock_cur.execute.side_effect = raise_error

    with patch("postgres.get_connection", return_value=mock_conn):
        with pytest.raises(postgres.UiPostgresError):
            with postgres.transaction() as cur:
                cur.execute("BAD SQL")


# ── app.py : pas d'import CxO ────────────────────────────────────────────────

def test_app_imports_no_cxo():
    cxo_path = UI_PATH / "views" / "cxo_search.py"
    search_path = UI_PATH / "search"
    assert not cxo_path.exists(), "cxo_search.py doit avoir été supprimé"
    assert not search_path.exists(), "ui/search/ doit avoir été supprimé"


# ── Navigation : pas de CxO Search ───────────────────────────────────────────

def test_app_views_no_cxo_search():
    import ast
    import ui as _  # noqa

    app_source = (UI_PATH / "app.py").read_text()
    tree = ast.parse(app_source)
    # Cherche le dict VIEWS dans l'AST
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "VIEWS":
                    keys = [
                        k.value if isinstance(k, ast.Constant) else ""
                        for k in node.value.keys
                    ]
                    assert "CxO Search" not in keys
                    assert "Cibles LinkedIn" in keys
                    assert "Posts LinkedIn" in keys
                    return
    pytest.fail("VIEWS dict not found in app.py")
